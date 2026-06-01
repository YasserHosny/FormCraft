import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTabsModule } from '@angular/material/tabs';
import { TranslateModule } from '@ngx-translate/core';
import { IntegrationService } from '../../../core/services/integration.service';

@Component({
  selector: 'fc-admin-integrations',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatSlideToggleModule,
    MatTabsModule,
    TranslateModule,
  ],
  templateUrl: './integrations.component.html',
  styleUrl: './integrations.component.scss',
})
export class IntegrationsComponent implements OnInit {
  private integrationService = inject(IntegrationService);

  activeTab = 0;
  credentials: any[] = [];
  webhooks: any[] = [];
  loading = true;
  error = false;

  credentialColumns = ['name', 'key_prefix', 'scopes', 'status', 'expires_at', 'actions'];
  webhookColumns = ['name', 'event_type', 'target_url', 'status', 'actions'];

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
        this.error = true;
      },
    });
  }

  loadWebhooks(): void {
    this.integrationService.listWebhooks().subscribe({
      next: (response: any) => {
        this.webhooks = response.items || [];
      },
      error: () => {
        this.error = true;
      },
    });
  }

  revokeCredential(credentialId: string): void {
    this.integrationService.revokeCredential(credentialId).subscribe({
      next: () => {
        this.loadCredentials();
      },
      error: () => {
        this.error = true;
      },
    });
  }

  toggleWebhook(webhook: any): void {
    const newStatus = webhook.status === 'active' ? 'paused' : 'active';
    this.integrationService.updateWebhook(webhook.id, { status: newStatus }).subscribe({
      next: () => {
        this.loadWebhooks();
      },
      error: () => {
        this.error = true;
      },
    });
  }

  canRevoke(credential: any): boolean {
    return credential.status === 'active';
  }

  canToggle(webhook: any): boolean {
    return webhook.status === 'active' || webhook.status === 'paused';
  }
}
