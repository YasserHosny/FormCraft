import { Component } from '@angular/core';

@Component({
  standalone: false,
  selector: 'app-platform-layout',
  template: `
    <div class="platform-layout">
      <app-context-switcher></app-context-switcher>
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [
    `.platform-layout { padding: 24px; }`,
  ],
})
export class PlatformLayoutComponent {}
