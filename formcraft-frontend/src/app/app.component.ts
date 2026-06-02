import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { Subject, filter, takeUntil } from 'rxjs';
import { LanguageService } from './core/i18n/language.service';
import { AuthService } from './core/auth/auth.service';
import { ThemePreferenceService } from './core/services/theme-preference.service';

@Component({
  selector: 'fc-root',
  standalone: false,
  template: `
    <ng-container *ngIf="isAuthenticated && !isRedesignRoute; else routeOnly">
      <fc-app-shell></fc-app-shell>
    </ng-container>
    <ng-template #routeOnly>
      <router-outlet></router-outlet>
    </ng-template>
    <fc-feedback-widget *ngIf="isAuthenticated" [class.spark-mode]="isRedesignRoute"></fc-feedback-widget>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
  `],
})
export class AppComponent implements OnInit, OnDestroy {
  isAuthenticated = false;
  isRedesignRoute = false;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private languageService: LanguageService,
    private authService: AuthService,
    private router: Router,
    private themePreference: ThemePreferenceService
  ) {
    // Subscribe in constructor (not ngOnInit) so the BehaviorSubject's
    // current value is reflected on the very first template render.
    // AuthService constructor already ran and set the value synchronously
    // from localStorage, so this gives us the correct state immediately,
    // preventing the #loginOnly router-outlet from ever being activated
    // when the user is already authenticated.
    this.authService.isAuthenticated$
      .pipe(takeUntil(this.destroy$))
      .subscribe((val) => {
        this.isAuthenticated = val;
      });
  }

  ngOnInit(): void {
    this.languageService.init();
    this.setThemeRoute(this.router.url);
    this.router.events
      .pipe(
        filter((event): event is NavigationEnd => event instanceof NavigationEnd),
        takeUntil(this.destroy$)
      )
      .subscribe((event) => this.setThemeRoute(event.urlAfterRedirects || event.url));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private setThemeRoute(url: string): void {
    this.isRedesignRoute = url === '/ui' || url.startsWith('/ui/');
  }
}
