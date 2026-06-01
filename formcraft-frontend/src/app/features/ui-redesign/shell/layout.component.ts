import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter, Subject, takeUntil } from 'rxjs';
import { BreakpointObserver } from '@angular/cdk/layout';
import { ToolbarComponent } from './toolbar.component';
import { SidebarComponent } from './sidebar.component';
import { DirectionService, Dir } from '../../../core/i18n/direction.service';

@Component({
  selector: 'fc-redesign-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, ToolbarComponent, SidebarComponent],
  template: `
    <div class="layout-wrapper" [attr.dir]="currentDir">
      <fc-redesign-toolbar
        [activeMode]="activeMode"
        (menuRequested)="toggleSidebar()">
      </fc-redesign-toolbar>
      <div class="layout-body" [class.sidebar-collapsed]="sidebarCollapsed">
        <fc-redesign-sidebar
          [mode]="activeMode"
          [open]="sidebarOpen"
          [collapsed]="sidebarCollapsed"
          (closed)="sidebarOpen = false">
        </fc-redesign-sidebar>
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
export class LayoutComponent implements OnDestroy {
  activeMode: 'studio' | 'desk' | 'admin' = 'studio';
  currentDir: 'rtl' | 'ltr' = 'rtl';
  sidebarOpen = false;
  sidebarCollapsed = false;
  private isPhone = false;

  private readonly destroy$ = new Subject<void>();

  constructor(
    private router: Router,
    private directionService: DirectionService,
    private breakpointObserver: BreakpointObserver,
  ) {
    this.currentDir = this.directionService.currentDir;

    this.breakpointObserver.observe('(max-width: 599px)')
      .pipe(takeUntil(this.destroy$))
      .subscribe((state) => {
        this.isPhone = state.matches;
        if (this.isPhone) {
          this.sidebarCollapsed = false;
        } else {
          this.sidebarOpen = false;
        }
      });

    this.directionService.dir$
      .pipe(takeUntil(this.destroy$))
      .subscribe((dir: Dir) => {
        this.currentDir = dir;
      });

    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      takeUntil(this.destroy$),
    ).subscribe(e => {
      this.detectMode(e.urlAfterRedirects);
      this.sidebarOpen = false;
    });
    this.detectMode(this.router.url);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  toggleSidebar(): void {
    if (this.isPhone) {
      this.sidebarOpen = !this.sidebarOpen;
      return;
    }

    this.sidebarCollapsed = !this.sidebarCollapsed;
    this.sidebarOpen = false;
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
