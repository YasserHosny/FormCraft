import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterModule } from '@angular/router';
import { BehaviorSubject } from 'rxjs';

import { AuthService, User } from '../../../core/auth/auth.service';
import { ToolbarComponent } from './toolbar.component';

describe('Redesign ToolbarComponent', () => {
  let fixture: ComponentFixture<ToolbarComponent>;

  beforeEach(async () => {
    const currentUser$ = new BehaviorSubject<User | null>({
      id: 'user-1',
      email: 'designer@example.com',
      role: 'designer',
      language: 'ar',
      display_name: 'مصمم حقيقي',
    });

    await TestBed.configureTestingModule({
      imports: [ToolbarComponent, RouterModule.forRoot([])],
      providers: [
        {
          provide: AuthService,
          useValue: {
            currentUser$: currentUser$.asObservable(),
            logout: jasmine.createSpy('logout'),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolbarComponent);
    fixture.detectChanges();
  });

  it('shows the authenticated user and exposes a classic theme route', () => {
    const text = fixture.nativeElement.textContent;
    const classicLink: HTMLAnchorElement | null =
      fixture.nativeElement.querySelector('a[href="/templates"]');

    expect(text).toContain('مصمم حقيقي');
    expect(classicLink).not.toBeNull();
  });
});
