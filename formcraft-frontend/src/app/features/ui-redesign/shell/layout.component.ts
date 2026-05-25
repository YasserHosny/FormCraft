import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { ToolbarComponent } from './toolbar.component';
import { SidebarComponent } from './sidebar.component';

@Component({
  selector: 'fc-redesign-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, ToolbarComponent, SidebarComponent],
  template: `
    <div class="layout-wrapper" dir="rtl">
      <fc-redesign-toolbar [activeMode]="activeMode"></fc-redesign-toolbar>
      <div class="layout-body">
        <fc-redesign-sidebar [mode]="activeMode"></fc-redesign-sidebar>
        <main class="layout-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .layout-wrapper {
      height: 100vh;
      display: flex;
      flex-direction: column;
      background: var(--fc-bg);
    }
    .layout-body {
      flex: 1;
      display: flex;
      overflow: hidden;
    }
    .layout-content {
      flex: 1;
      overflow: auto;
      display: flex;
      flex-direction: column;
    }
  `],
})
export class LayoutComponent {
  activeMode: 'studio' | 'desk' | 'admin' = 'studio';

  constructor(private router: Router) {
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd)
    ).subscribe(e => {
      this.detectMode(e.urlAfterRedirects);
    });
    this.detectMode(this.router.url);
  }

  private detectMode(url: string): void {
    if (url.includes('/ui/admin')) {
      this.activeMode = 'admin';
    } else if (url.includes('/ui/desk')) {
      this.activeMode = 'desk';
    } else {
      this.activeMode = 'studio';
    }
  }
}
