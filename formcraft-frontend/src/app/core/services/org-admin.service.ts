import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

/* ------------------------------------------------------------------ */
/*  Interfaces                                                         */
/* ------------------------------------------------------------------ */

export interface OrgSettings {
  id: string;
  name_ar: string;
  name_en: string;
  logo_url: string | null;
  primary_color: string;
  custom_domain: string | null;
  subscription_tier: string;
  default_language: 'ar' | 'en';
  default_country: string;
  default_currency: string;
  settings: OrgFeatureSettings;
}

export interface OrgFeatureSettings {
  approval_workflow: boolean;
  hijri_date_support: boolean;
  draft_expiry_days: number;
  data_retention_months: number;
  max_batch_size: number;
}

export interface Department {
  id: string;
  name_ar: string;
  name_en: string;
  is_active: boolean;
  branch_count: number;
  user_count: number;
}

export interface DepartmentPayload {
  name_ar: string;
  name_en: string;
}

export interface Branch {
  id: string;
  department_id: string;
  name_ar: string;
  name_en: string;
  location: string | null;
  is_active: boolean;
  user_count: number;
}

export interface BranchPayload {
  name_ar: string;
  name_en: string;
  location?: string;
}

export interface OrgUser {
  id: string;
  email: string;
  display_name: string | null;
  role: string;
  department_id: string | null;
  department_name: string | null;
  branch_id: string | null;
  branch_name: string | null;
  is_active: boolean;
  last_login: string | null;
}

export interface UserAssignment {
  role?: string;
  department_id?: string | null;
  branch_id?: string | null;
}

export interface Invitation {
  id: string;
  email: string;
  role: string;
  department_id: string | null;
  department_name: string | null;
  branch_id: string | null;
  branch_name: string | null;
  status: 'pending' | 'accepted' | 'expired';
  expires_at: string;
  created_at: string;
}

export interface InvitationPayload {
  email: string;
  role: string;
  department_id?: string;
  branch_id?: string;
}

export interface InvitationInfo {
  org_name: string;
  role: string;
  email: string;
}

export interface InvitationAcceptPayload {
  display_name: string;
  password: string;
}

export interface OrgBranding {
  name_ar: string;
  name_en: string;
  logo_url: string | null;
  primary_color: string;
}

export interface UserListParams {
  department_id?: string;
  branch_id?: string;
  role?: string;
  is_active?: boolean;
}

/* ------------------------------------------------------------------ */
/*  Service                                                            */
/* ------------------------------------------------------------------ */

@Injectable({ providedIn: 'root' })
export class OrgAdminService {
  private base = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  /* ---------- Org Settings ---------- */

  getOrgSettings(): Observable<OrgSettings> {
    return this.http.get<OrgSettings>(`${this.base}/org-settings`);
  }

  updateOrgSettings(data: Partial<OrgSettings>): Observable<OrgSettings> {
    return this.http.patch<OrgSettings>(`${this.base}/org-settings`, data);
  }

  uploadLogo(file: File): Observable<{ logo_url: string }> {
    const fd = new FormData();
    fd.append('file', file);
    return this.http.post<{ logo_url: string }>(`${this.base}/org-settings/logo`, fd);
  }

  /* ---------- Departments ---------- */

  getDepartments(): Observable<Department[]> {
    return this.http.get<Department[]>(`${this.base}/departments`);
  }

  createDepartment(data: DepartmentPayload): Observable<Department> {
    return this.http.post<Department>(`${this.base}/departments`, data);
  }

  updateDepartment(id: string, data: DepartmentPayload): Observable<Department> {
    return this.http.patch<Department>(`${this.base}/departments/${id}`, data);
  }

  deactivateDepartment(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/departments/${id}`);
  }

  /* ---------- Branches ---------- */

  getBranchesByDepartment(departmentId: string): Observable<Branch[]> {
    return this.http.get<Branch[]>(`${this.base}/departments/${departmentId}/branches`);
  }

  createBranch(departmentId: string, data: BranchPayload): Observable<Branch> {
    return this.http.post<Branch>(`${this.base}/departments/${departmentId}/branches`, data);
  }

  getAllBranches(): Observable<Branch[]> {
    return this.http.get<Branch[]>(`${this.base}/branches`);
  }

  updateBranch(id: string, data: BranchPayload): Observable<Branch> {
    return this.http.patch<Branch>(`${this.base}/branches/${id}`, data);
  }

  deactivateBranch(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/branches/${id}`);
  }

  /* ---------- Users ---------- */

  getUsers(params?: UserListParams): Observable<OrgUser[]> {
    let httpParams = new HttpParams();
    if (params?.department_id) httpParams = httpParams.set('department_id', params.department_id);
    if (params?.branch_id) httpParams = httpParams.set('branch_id', params.branch_id);
    if (params?.role) httpParams = httpParams.set('role', params.role);
    if (params?.is_active !== undefined) httpParams = httpParams.set('is_active', String(params.is_active));
    return this.http.get<OrgUser[]>(`${this.base}/users`, { params: httpParams });
  }

  updateUser(id: string, data: UserAssignment): Observable<OrgUser> {
    return this.http.patch<OrgUser>(`${this.base}/users/${id}`, data);
  }

  deactivateUser(id: string): Observable<void> {
    return this.http.post<void>(`${this.base}/users/${id}/deactivate`, {});
  }

  activateUser(id: string): Observable<void> {
    return this.http.post<void>(`${this.base}/users/${id}/activate`, {});
  }

  /* ---------- Invitations ---------- */

  getInvitations(): Observable<Invitation[]> {
    return this.http.get<Invitation[]>(`${this.base}/invitations`);
  }

  createInvitation(data: InvitationPayload): Observable<Invitation> {
    return this.http.post<Invitation>(`${this.base}/invitations`, data);
  }

  cancelInvitation(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/invitations/${id}`);
  }

  getInvitationInfo(token: string): Observable<InvitationInfo> {
    return this.http.get<InvitationInfo>(`${this.base}/invitations/${token}`);
  }

  acceptInvitation(token: string, data: InvitationAcceptPayload): Observable<void> {
    return this.http.post<void>(`${this.base}/invitations/accept/${token}`, data);
  }

  /* ---------- Branding ---------- */

  getBranding(domain: string): Observable<OrgBranding> {
    return this.http.get<OrgBranding>(`${this.base}/branding/${domain}`);
  }
}
