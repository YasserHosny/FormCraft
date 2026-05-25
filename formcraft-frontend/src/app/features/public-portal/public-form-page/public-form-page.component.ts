import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { PortalService } from '../../../core/services/portal.service';
import { PublicFormSession, PublicSubmissionRequest } from '../../../shared/models/portal.models';

@Component({
  selector: 'fc-public-form-page',
  standalone: false,
  templateUrl: './public-form-page.component.html',
  styleUrls: ['./public-form-page.component.scss'],
})
export class PublicFormPageComponent implements OnInit {
  session: PublicFormSession | null = null;
  sessionToken = '';
  fieldValues: Record<string, any> = {};
  validationErrors: Record<string, string> = {};
  isSubmitting = false;
  submitted = false;
  error: string | null = null;
  language: 'ar' | 'en' = 'ar';
  dir: 'rtl' | 'ltr' = 'rtl';
  tafqeetMap: Record<string, string> = {};
  showOtpGate = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private portalService: PortalService,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const orgSlug = params['org'];
      const publicSlug = params['slug'];
      if (orgSlug && publicSlug) {
        this.loadForm(orgSlug, publicSlug);
      }
    });
    this.language = (this.translate.currentLang as 'ar' | 'en') || 'ar';
    this.dir = this.language === 'ar' ? 'rtl' : 'ltr';
  }

  loadForm(orgSlug: string, publicSlug: string): void {
    this.portalService.loadPublicForm(orgSlug, publicSlug).subscribe({
      next: (session) => {
        this.session = session;
        this.sessionToken = session.session_token;
        this.language = session.language_default || 'ar';
        this.dir = this.language === 'ar' ? 'rtl' : 'ltr';
        if (session.settings.otp_required) {
          this.showOtpGate = true;
        }
      },
      error: () => {
        this.error = this.translate.instant('publicPortal.validationError');
      },
    });
  }

  onOtpVerified(): void {
    this.showOtpGate = false;
  }

  toggleLanguage(): void {
    this.language = this.language === 'ar' ? 'en' : 'ar';
    this.dir = this.language === 'ar' ? 'rtl' : 'ltr';
    this.translate.use(this.language);
  }

  onFieldChange(key: string, value: any): void {
    this.fieldValues[key] = value;
    if (this.validationErrors[key]) {
      delete this.validationErrors[key];
    }
  }

  submit(): void {
    if (!this.sessionToken || this.isSubmitting) return;
    this.isSubmitting = true;
    this.error = null;

    const request: PublicSubmissionRequest = {
      field_values: this.fieldValues,
      captcha_token: null,
    };

    this.portalService.submitPublicForm(this.sessionToken, request).subscribe({
      next: (response) => {
        this.isSubmitting = false;
        this.submitted = true;
        this.router.navigate(['/forms', this.route.snapshot.params['org'], this.route.snapshot.params['slug'], 'confirmation'], {
          queryParams: {
            ref: response.reference_number,
            pdf: response.pdf_download_url,
            emailStatus: response.email_confirmation_status,
          },
        });
      },
      error: (err) => {
        this.isSubmitting = false;
        if (err?.error?.detail?.validation_errors) {
          const errs: any[] = err.error.detail.validation_errors;
          this.validationErrors = errs.reduce((acc, e) => {
            acc[e.field] = e.error;
            return acc;
          }, {} as Record<string, string>);
          this.error = this.translate.instant('publicPortal.validationError');
        } else {
          this.error = err?.error?.detail || this.translate.instant('publicPortal.validationError');
        }
      },
    });
  }
}
