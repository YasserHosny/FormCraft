import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable, of } from 'rxjs';
import { catchError, filter, map, take } from 'rxjs/operators';
import { AuthService } from '../auth/auth.service';

@Injectable({ providedIn: 'root' })
export class PlatformAdminGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}

  canActivate(): Observable<boolean | UrlTree> {
    return this.auth.currentUser$.pipe(
      filter((user) => user !== null),
      take(1),
      map((user) => {
        if (user?.is_platform_admin) {
          return true;
        }
        return this.router.createUrlTree(['/']);
      }),
      catchError(() => of(this.router.createUrlTree(['/'])))
    );
  }
}
