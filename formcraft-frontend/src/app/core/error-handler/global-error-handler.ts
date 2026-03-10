import { ErrorHandler, Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  constructor(private snackBar: MatSnackBar) {}

  handleError(error: unknown): void {
    console.error('Unhandled error:', error);

    const httpError = error as { status?: number };
    if (httpError?.status) {
      this.snackBar.open(
        `Server error (${httpError.status}). Please try again.`,
        'Dismiss',
        { duration: 5000 }
      );
    } else {
      this.snackBar.open('An unexpected error occurred.', 'Dismiss', {
        duration: 5000,
      });
    }
  }
}
