import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, Subject } from 'rxjs';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';

import { AuthService } from './core/auth/auth.service';
import { LanguageService } from './core/i18n/language.service';
import { AppComponent } from './app.component';

@Component({ selector: 'fc-app-shell', template: '<span>classic shell</span>', standalone: false })
class AppShellStubComponent {}

@Component({ selector: 'fc-feedback-widget', template: '<span>feedback</span>', standalone: false })
class FeedbackWidgetStubComponent {}

describe('AppComponent theme shell selection', () => {
  let fixture: ComponentFixture<AppComponent>;
  let routerEvents$: Subject<unknown>;
  let routerStub: { url: string; events: Subject<unknown> };
  let authState$: BehaviorSubject<boolean>;

  beforeEach(async () => {
    routerEvents$ = new Subject<unknown>();
    routerStub = {
      url: '/ui/studio/templates',
      events: routerEvents$,
    };
    authState$ = new BehaviorSubject(true);

    await TestBed.configureTestingModule({
      declarations: [AppComponent, AppShellStubComponent, FeedbackWidgetStubComponent],
      imports: [RouterOutlet],
      providers: [
        {
          provide: AuthService,
          useValue: {
            isAuthenticated$: authState$,
          },
        },
        { provide: LanguageService, useValue: { init: jasmine.createSpy('init') } },
        { provide: Router, useValue: routerStub },
      ],
    }).compileComponents();
  });

  it('does not wrap redesign routes in the classic app shell', () => {
    fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('fc-app-shell')).toBeNull();
  });

  it('wraps classic authenticated routes in the classic app shell', () => {
    routerStub.url = '/templates';

    fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('fc-app-shell')).not.toBeNull();
  });

  it('updates shell selection after navigation', () => {
    routerStub.url = '/templates';
    fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('fc-app-shell')).not.toBeNull();

    routerEvents$.next(new NavigationEnd(1, '/ui/studio/templates', '/ui/studio/templates'));
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('fc-app-shell')).toBeNull();
  });
});
