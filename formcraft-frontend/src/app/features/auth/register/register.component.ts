import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';
import { TranslateService } from '@ngx-translate/core';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'fc-register',
  standalone: false,
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
})
export class RegisterComponent {
  registerForm: FormGroup;
  loading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      display_name: [''],
      role: ['viewer', Validators.required],
    });
  }

  onSubmit(): void {
    if (this.registerForm.invalid) return;
    this.loading = true;
    this.errorMessage = '';

    this.http
      .post(`${environment.apiBaseUrl}/auth/register`, this.registerForm.value)
      .subscribe({
        next: () => {
          this.loading = false;
          this.snackBar.open('User registered successfully', '', {
            duration: 3000,
          });
          this.router.navigate(['/templates']);
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage =
            err.error?.detail || 'Failed to register user';
        },
      });
  }
}
