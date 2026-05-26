import { ErrorHandler, Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  constructor(private snackBar: MatSnackBar) {}

  handleError(error: unknown): void {
    // Unwrap zone.js wrapper if present
    const original = (error as any)?.rejection ?? error;
    console.error('Unhandled error:', original);

    // Only show snackbar for genuine HTTP errors (4xx / 5xx)
    if (original instanceof HttpErrorResponse && original.status >= 400) {
      this.snackBar.open(
        `Server error (${original.status}). Please try again.`,
        'Dismiss',
        { duration: 5000 }
      );
    }
    // Silently log all other errors (Angular internal, 200 parse failures, etc.)
  }
}
