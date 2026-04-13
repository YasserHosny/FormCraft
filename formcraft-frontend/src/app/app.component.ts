import { Component, OnInit } from '@angular/core';
import { LanguageService } from './core/i18n/language.service';
import { AuthService } from './core/auth/auth.service';

@Component({
  selector: 'fc-root',
  standalone: false,
  template: `
    <ng-container *ngIf="isAuthenticated; else loginOnly">
      <fc-app-shell></fc-app-shell>
    </ng-container>
    <ng-template #loginOnly>
      <router-outlet></router-outlet>
    </ng-template>
  `,
  styles: [`
    :host {
      display: block;
      height: 100%;
    }
  `],
})
export class AppComponent implements OnInit {
  isAuthenticated = false;

  constructor(
    private languageService: LanguageService,
    private authService: AuthService
  ) {
    // Subscribe in constructor (not ngOnInit) so the BehaviorSubject's
    // current value is reflected on the very first template render.
    // AuthService constructor already ran and set the value synchronously
    // from localStorage, so this gives us the correct state immediately,
    // preventing the #loginOnly router-outlet from ever being activated
    // when the user is already authenticated.
    this.authService.isAuthenticated$.subscribe((val) => {
      this.isAuthenticated = val;
    });
  }

  ngOnInit(): void {
    this.languageService.init();
  }
}
