import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';

@Component({
  selector: 'fc-app-shell',
  standalone: false,
  template: `
    <mat-toolbar color="primary" class="app-toolbar">
      <span class="app-title" routerLink="/templates">FormCraft</span>
      <span class="spacer"></span>

      <ng-container *ngIf="user">
        <button mat-button routerLink="/templates">
          {{ 'templates.title' | translate }}
        </button>
        <button
          mat-button
          routerLink="/auth/register"
          *ngIf="user.role === 'admin'"
        >
          {{ 'auth.register' | translate }}
        </button>

        <button mat-icon-button [matMenuTriggerFor]="userMenu">
          <mat-icon>account_circle</mat-icon>
        </button>
        <mat-menu #userMenu="matMenu">
          <div mat-menu-item disabled class="user-info">
            {{ user.display_name || user.email }}
            <br />
            <small>{{ 'roles.' + user.role | translate }}</small>
          </div>
          <mat-divider></mat-divider>
          <button mat-menu-item routerLink="/auth/profile">
            <mat-icon>person</mat-icon>
            {{ 'auth.profile' | translate }}
          </button>
          <button mat-menu-item (click)="toggleLanguage()">
            <mat-icon>language</mat-icon>
            {{ currentLang === 'ar' ? 'English' : 'العربية' }}
          </button>
          <mat-divider></mat-divider>
          <button mat-menu-item (click)="logout()">
            <mat-icon>logout</mat-icon>
            {{ 'auth.logout' | translate }}
          </button>
        </mat-menu>
      </ng-container>
    </mat-toolbar>

    <div class="shell-content">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .app-toolbar {
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .app-title {
      cursor: pointer;
      font-weight: 700;
      font-size: 18px;
    }
    .spacer {
      flex: 1 1 auto;
    }
    .shell-content {
      height: calc(100vh - 64px);
      overflow: auto;
    }
    .user-info {
      line-height: 1.4;
      opacity: 0.9;
    }
  `],
})
export class AppShellComponent implements OnInit {
  user: User | null = null;
  currentLang = 'ar';

  constructor(
    private authService: AuthService,
    private languageService: LanguageService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe((u) => {
      this.user = u;
    });
    this.currentLang = this.languageService.getLanguage();
  }

  toggleLanguage(): void {
    this.languageService.toggleLanguage();
    this.currentLang = this.languageService.getLanguage();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }
}
