import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { Observable, filter, map, take } from 'rxjs';
import { AuthService } from './auth.service';
import { getDefaultRouteForRole } from '../../shared/components/app-shell/app-shell.component';

@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean> {
    const requiredRoles = route.data['roles'] as string[];
    return this.authService.currentUser$.pipe(
      // Wait until loadProfile() resolves — null means not yet loaded
      filter((user) => user !== null),
      take(1),
      map((user) => {
        if (!user || !requiredRoles.includes(user.role)) {
          // F15: Redirect to role-appropriate default mode instead of /templates
          this.router.navigate([getDefaultRouteForRole(user?.role || 'operator')]);
          return false;
        }
        return true;
      })
    );
  }
}
