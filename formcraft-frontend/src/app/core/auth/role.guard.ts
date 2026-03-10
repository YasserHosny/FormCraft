import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { Observable, map, take } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean> {
    const requiredRoles = route.data['roles'] as string[];
    return this.authService.currentUser$.pipe(
      take(1),
      map((user) => {
        if (!user || !requiredRoles.includes(user.role)) {
          this.router.navigate(['/templates']);
          return false;
        }
        return true;
      })
    );
  }
}
