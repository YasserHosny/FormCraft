import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { take, filter } from 'rxjs';
import { AuthService } from '../../../core/auth/auth.service';
import { OrgAdminService, OrgBranding } from '../../../core/services/org-admin.service';
import { ThemePreferenceService } from '../../../core/services/theme-preference.service';
import { environment } from '../../../../environments/environment';

interface OrgOption {
  id: string;
  name: string;
  logo_url: string | null;
}

@Component({
  selector: 'fc-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  errorMessage = '';

  /** T044: org selection after login */
  showOrgSelector = false;
  orgOptions: OrgOption[] = [];
  selectedOrgId = '';

  /** T045: custom domain branding */
  branding: OrgBranding | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private orgAdmin: OrgAdminService,
    private http: HttpClient,
    private router: Router,
    private themePreference: ThemePreferenceService,
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
    });
  }

  ngOnInit(): void {
    // T045: If running on a custom domain, fetch branding
    const host = window.location.hostname;
    if (host !== 'localhost' && !host.includes('formcraft')) {
      this.orgAdmin.getBranding(host).subscribe({
        next: (b) => (this.branding = b),
        error: () => {}, // ignore — default branding
      });
    }
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;
    this.loading = true;
    this.errorMessage = '';

    const { email, password } = this.loginForm.value;
    this.authService.login(email, password).subscribe({
      next: (response: any) => {
        this.loading = false;
        // T044: Check if multi-org selection is required
        if (response.requires_org_selection && response.organizations) {
          this.orgOptions = response.organizations;
          this.showOrgSelector = true;
        } else {
          // F15: Redirect to role-based default mode
          this.navigateToRoleDefault();
        }
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Invalid email or password';
      },
    });
  }

  selectOrg(orgId: string): void {
    this.loading = true;
    this.authService.selectOrg(orgId).subscribe({
      next: () => {
        this.loading = false;
        // F15: Redirect to role-based default mode
        this.navigateToRoleDefault();
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Organization selection failed';
      },
    });
  }

  /** F15: Wait for user profile to load, then redirect to their role's default route. */
  private navigateToRoleDefault(): void {
    this.authService.currentUser$.pipe(
      filter((u) => u !== null),
      take(1),
    ).subscribe((user) => {
      const theme = this.themePreference.getPreference();
      const route = this.themePreference.getDefaultRoute(theme, user!.role);
      this.router.navigate([route]);
    });
  }
}
