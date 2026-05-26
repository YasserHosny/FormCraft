import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-context-switcher',
  template: `
    <mat-form-field appearance="outline" class="context-switcher" *ngIf="showSwitcher">
      <mat-label>{{ 'PLATFORM.CONTEXT_LABEL' | translate }}</mat-label>
      <mat-select [value]="currentContext" (selectionChange)="switchContext($event.value)">
        <mat-option value="platform">{{ 'PLATFORM.CONTEXT_PLATFORM' | translate }}</mat-option>
        <mat-option value="org">{{ 'PLATFORM.CONTEXT_ORG' | translate }}</mat-option>
      </mat-select>
    </mat-form-field>
  `,
  styles: [
    `.context-switcher { margin-bottom: 16px; width: 200px; }`,
  ],
})
export class ContextSwitcherComponent {
  showSwitcher = false;
  currentContext: 'platform' | 'org' = 'platform';

  constructor(private auth: AuthService, private router: Router) {
    this.auth.getCurrentUser().subscribe((user) => {
      this.showSwitcher = !!(user?.is_platform_admin && user?.org_id);
      this.currentContext = this.router.url.startsWith('/platform') ? 'platform' : 'org';
    });
  }

  switchContext(context: 'platform' | 'org'): void {
    if (context === 'platform') {
      this.router.navigate(['/platform']);
    } else {
      this.router.navigate(['/admin']);
    }
  }
}
