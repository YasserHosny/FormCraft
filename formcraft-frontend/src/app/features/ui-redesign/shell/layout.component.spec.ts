import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { NavigationEnd, Router } from '@angular/router';
import { BehaviorSubject, Subject } from 'rxjs';
import { BreakpointObserver, BreakpointState } from '@angular/cdk/layout';

import { DirectionService } from '../../../core/i18n/direction.service';
import { LayoutComponent } from './layout.component';
import { SidebarComponent } from './sidebar.component';
import { ToolbarComponent } from './toolbar.component';

@Component({
  selector: 'fc-redesign-toolbar',
  standalone: true,
  template: '',
})
class ToolbarStubComponent {
  @Input() activeMode: 'studio' | 'desk' | 'admin' = 'studio';
  @Output() menuRequested = new EventEmitter<void>();
}

@Component({
  selector: 'fc-redesign-sidebar',
  standalone: true,
  template: '',
})
class SidebarStubComponent {
  @Input() mode: 'studio' | 'desk' | 'admin' = 'studio';
  @Input() open = false;
  @Input() collapsed = false;
  @Output() closed = new EventEmitter<void>();
}

describe('Redesign LayoutComponent', () => {
  let fixture: ComponentFixture<LayoutComponent>;
  let routerEvents$: Subject<NavigationEnd>;
  let phoneState$: BehaviorSubject<BreakpointState>;

  beforeEach(async () => {
    routerEvents$ = new Subject<NavigationEnd>();
    phoneState$ = new BehaviorSubject<BreakpointState>({ matches: false, breakpoints: {} });

    await TestBed.configureTestingModule({
      imports: [LayoutComponent],
      providers: [
        {
          provide: Router,
          useValue: {
            url: '/ui/studio/templates',
            events: routerEvents$.asObservable(),
          },
        },
        {
          provide: DirectionService,
          useValue: {
            currentDir: 'ltr',
            dir$: new Subject<'rtl' | 'ltr'>().asObservable(),
          },
        },
        {
          provide: BreakpointObserver,
          useValue: {
            observe: () => phoneState$.asObservable(),
          },
        },
      ],
    })
      .overrideComponent(LayoutComponent, {
        remove: { imports: [ToolbarComponent, SidebarComponent] },
        add: { imports: [ToolbarStubComponent, SidebarStubComponent] },
      })
      .compileComponents();

    fixture = TestBed.createComponent(LayoutComponent);
    fixture.detectChanges();
  });

  it('toggles the desktop sidebar when the toolbar menu button is requested', () => {
    const toolbar = fixture.debugElement.query(By.directive(ToolbarStubComponent)).componentInstance as ToolbarStubComponent;
    const body = fixture.nativeElement.querySelector('.layout-body') as HTMLElement;

    expect(body.classList).not.toContain('sidebar-collapsed');

    toolbar.menuRequested.emit();
    fixture.detectChanges();
    expect(body.classList).toContain('sidebar-collapsed');

    toolbar.menuRequested.emit();
    fixture.detectChanges();
    expect(body.classList).not.toContain('sidebar-collapsed');
  });

  it('opens the mobile drawer instead of collapsing the desktop sidebar on phones', () => {
    const toolbar = fixture.debugElement.query(By.directive(ToolbarStubComponent)).componentInstance as ToolbarStubComponent;
    const sidebar = fixture.debugElement.query(By.directive(SidebarStubComponent)).componentInstance as SidebarStubComponent;

    phoneState$.next({ matches: true, breakpoints: {} });
    toolbar.menuRequested.emit();
    fixture.detectChanges();

    expect(sidebar.open).toBeTrue();
    expect(sidebar.collapsed).toBeFalse();
  });
});
