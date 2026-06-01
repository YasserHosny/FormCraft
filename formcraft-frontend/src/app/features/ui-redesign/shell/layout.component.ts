import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { filter, Subject, takeUntil } from 'rxjs';
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
        (menuRequested)="sidebarOpen = true">
      </fc-redesign-toolbar>
      <div class="layout-body">
        <fc-redesign-sidebar
          [mode]="activeMode"
          [open]="sidebarOpen"
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

  private destroy$ = new Subject<void>();

  constructor(private router: Router, private directionService: DirectionService) {
    this.currentDir = this.directionService.currentDir;

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
