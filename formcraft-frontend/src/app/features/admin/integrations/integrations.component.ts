import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { IntegrationService } from '../../../core/services/integration.service';

@Component({
  selector: 'fc-integrations',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    TranslateModule,
  ],
  templateUrl: './integrations.component.html',
  styleUrls: ['./integrations.component.scss'],
})
export class IntegrationsComponent implements OnInit {
  activeTab = 0;
  credentials: any[] = [];
  webhooks: any[] = [];
  loading = true;

  constructor(
    private integrationService: IntegrationService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadCredentials();
    this.loadWebhooks();
  }

  loadCredentials(): void {
    this.integrationService.listCredentials().subscribe({
      next: (response: any) => {
        this.credentials = response.items || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  loadWebhooks(): void {
    this.integrationService.listWebhooks().subscribe({
      next: (response: any) => {
        this.webhooks = response.items || [];
      },
      error: () => {},
    });
  }

  revokeCredential(credentialId: string): void {
    if (!confirm('Revoke this credential?')) return;
    this.integrationService.revokeCredential(credentialId).subscribe({
      next: () => {
        this.snackBar.open('Credential revoked', '', { duration: 3000 });
        this.loadCredentials();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Revoke failed', '', { duration: 3000 });
      },
    });
  }

  toggleWebhook(webhook: any): void {
    const newStatus = webhook.status === 'active' ? 'paused' : 'active';
    this.integrationService.updateWebhook(webhook.id, { status: newStatus }).subscribe({
      next: () => {
        this.snackBar.open('Webhook updated', '', { duration: 3000 });
        this.loadWebhooks();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Update failed', '', { duration: 3000 });
      },
    });
  }
}