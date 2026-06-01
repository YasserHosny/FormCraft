import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

/** URL fragments that must never trigger a 401-redirect (would cause a loop). */
const AUTH_URLS = ['/auth/login', '/auth/refresh', '/auth/register'];

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  intercept(
    req: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    const token = this.authService.getToken();
    const cloned = token
      ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
      : req;

    return next.handle(cloned).pipe(
      catchError((error: unknown) => {
        if (
          error instanceof HttpErrorResponse &&
          error.status === 401 &&
          !AUTH_URLS.some((u) => req.url.includes(u))
        ) {
          // Session expired or token invalid — wipe local state and go to login.
          // We use forceLogout() (no HTTP call) to avoid triggering another 401.
          this.authService.forceLogout();
          this.router.navigate(['/auth/login'], {
            queryParams: { returnUrl: this.router.url },
            replaceUrl: true,
          });
        }
        return throwError(() => error);
      }),
    );
  }
}
