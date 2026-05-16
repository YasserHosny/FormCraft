import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { filter } from 'rxjs/operators';
import { AuthService, User } from '../../../core/auth/auth.service';
import { ModeService } from '../../../core/navigation/mode.service';
import { ModeConfig } from '../../../core/navigation/mode.config';

@Component({
  selector: 'fc-mode-tabs',
  templateUrl: './mode-tabs.component.html',
  styleUrls: ['./mode-tabs.component.scss'],
})
export class ModeTabsComponent implements OnInit, OnDestroy {
  permittedModes: ModeConfig[] = [];
  activeMode: ModeConfig | null = null;
  user: User | null = null;
  mobileMenuOpen = false;

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private modeService: ModeService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        this.user = user;
        if (user) {
          this.permittedModes = this.modeService.getPermittedModes(user.role);
        } else {
          this.permittedModes = [];
        }
      });

    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        takeUntil(this.destroy$),
      )
      .subscribe((event) => {
        const url = (event as NavigationEnd).urlAfterRedirects || (event as NavigationEnd).url;
        this.activeMode = this.modeService.getActiveMode(url);
        this.mobileMenuOpen = false;
      });

    this.activeMode = this.modeService.getActiveMode(this.router.url);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onTabClick(mode: ModeConfig): void {
    if (this.activeMode?.id === mode.id) return;
    this.modeService.savePreference(mode.id);
    this.router.navigate([mode.defaultRoute]);
  }

  toggleMobileMenu(): void {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }
}