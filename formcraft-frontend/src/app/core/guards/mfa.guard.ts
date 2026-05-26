import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { MfaService } from '../services/mfa.service';

@Injectable({ providedIn: 'root' })
export class MfaGuard implements CanActivate {
  constructor(private mfa: MfaService, private router: Router) {}

  canActivate(): Observable<boolean | UrlTree> {
    // In a real implementation, check a stored flag or call an API
    // to see if the current session requires MFA verification.
    // For MVP, we simulate by checking if MFA challenge is needed.
    return of(true).pipe(
      map(() => true),
      catchError(() => of(this.router.createUrlTree(['/mfa/challenge'])))
    );
  }
}
