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
  ) {}

  ngOnInit(): void {
    this.languageService.init();
    this.authService.isAuthenticated$.subscribe((val) => {
      this.isAuthenticated = val;
    });
  }
}
