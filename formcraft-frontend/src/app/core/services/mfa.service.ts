import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MfaEnrollment {
  enrollment_id: string;
  method_type: 'totp' | 'sms' | 'email';
  qr_code_uri?: string;
}

export interface MfaVerifyResponse {
  is_verified: boolean;
  recovery_codes?: string[];
}

export interface MfaChallenge {
  challenge_id: string;
  method_type: 'totp' | 'sms' | 'email';
  expires_at: string;
}

@Injectable({ providedIn: 'root' })
export class MfaService {
  private readonly api = '/api/v1/mfa';

  constructor(private http: HttpClient) {}

  enroll(methodType: 'totp' | 'sms' | 'email', phoneNumber?: string): Observable<MfaEnrollment> {
    return this.http.post<MfaEnrollment>(`${this.api}/enroll`, { method_type: methodType, phone_number: phoneNumber });
  }

  verifyEnrollment(enrollmentId: string, code: string): Observable<MfaVerifyResponse> {
    return this.http.post<MfaVerifyResponse>(`${this.api}/enroll/${enrollmentId}/verify`, { code });
  }

  challenge(): Observable<MfaChallenge> {
    return this.http.post<MfaChallenge>(`${this.api}/challenge`, {});
  }

  verifyChallenge(challengeId: string, code: string): Observable<{ token: string }> {
    return this.http.post<{ token: string }>(`${this.api}/challenge/${challengeId}/verify`, { code });
  }

  recover(recoveryCode: string): Observable<{ token: string; remaining_codes: number }> {
    return this.http.post<{ token: string; remaining_codes: number }>(`${this.api}/recovery`, { recovery_code: recoveryCode });
  }
}
