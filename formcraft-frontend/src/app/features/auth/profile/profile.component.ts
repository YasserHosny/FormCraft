import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { environment } from '../../../../environments/environment';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'fc-profile',
  standalone: false,
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;
  saving = false;
  roleName = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private languageService: LanguageService,
    private translate: TranslateService,
    private snackBar: MatSnackBar,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.profileForm = this.fb.group({
      email: [{ value: '', disabled: true }],
      display_name: [''],
      language: ['ar'],
    });

    this.authService.currentUser$.subscribe((user) => {
      if (user) {
        this.profileForm.patchValue({
          email: user.email,
          display_name: user.display_name || '',
          language: user.language,
        });
        this.translate.get(`roles.${user.role}`).subscribe((name) => {
          this.roleName = name;
        });
        this.profileForm.markAsPristine();
      }
    });
  }

  onSave(): void {
    if (this.profileForm.pristine) return;
    this.saving = true;

    const { display_name, language } = this.profileForm.getRawValue();
    this.http
      .put(`${environment.apiBaseUrl}/users/me`, { display_name, language })
      .subscribe({
        next: () => {
          this.saving = false;
          this.languageService.setLanguage(language);
          this.profileForm.markAsPristine();
          this.snackBar.open(
            this.translate.instant('common.save') + ' ✓',
            '',
            { duration: 2000 }
          );
        },
        error: () => {
          this.saving = false;
          this.snackBar.open('Error saving profile', 'Dismiss', {
            duration: 3000,
          });
        },
      });
  }
}
