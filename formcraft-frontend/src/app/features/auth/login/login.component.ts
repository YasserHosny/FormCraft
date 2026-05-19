import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../../core/auth/auth.service';
import { OrgAdminService, OrgBranding } from '../../../core/services/org-admin.service';
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
          this.router.navigate(['/templates']);
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
        this.router.navigate(['/templates']);
      },
      error: () => {
        this.loading = false;
        this.errorMessage = 'Organization selection failed';
      },
    });
  }
}
