import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, filter, map, take, tap } from 'rxjs';
import { AuthService } from '../auth/auth.service';
import { ModeService } from './mode.service';
import { MODES } from './mode.config';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';

@Injectable({ providedIn: 'root' })
export class ModeGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private modeService: ModeService,
    private router: Router,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
    const targetMode = MODES.find((m) => state.url.startsWith(m.routePrefix));
    return this.authService.currentUser$.pipe(
      filter((user) => user !== null),
      take(1),
      map((user) => {
        if (!user) return false;
        if (!targetMode) return true;
        if (targetMode.permittedRoles.includes(user.role)) return true;
        const defaultMode = this.modeService.getDefaultMode(user.role, user.preferred_mode);
        this.snackBar.open(this.translate.instant('errors.unauthorized_mode'), undefined, {
          duration: 3000,
        });
        this.router.navigate([defaultMode.defaultRoute]);
        return false;
      }),
    );
  }
}