import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { NotificationItem } from '../../services/desk.service';

@Component({
  selector: 'fc-version-notifications',
  standalone: true,
  imports: [CommonModule, TranslateModule, MatButtonModule, MatIconModule],
  template: `
    <h2 class="section-title">{{ 'desk.section_notifications' | translate }}</h2>
    <div class="notification-list">
      <div *ngFor="let notification of notifications" class="notification-card">
        <div class="notification-content">
          <mat-icon class="notification-icon">update</mat-icon>
          <span class="notification-text">
            {{ 'desk.notification_updated' | translate:{ name: notification.template_name, version: notification.new_version } }}
          </span>
        </div>
        <div class="notification-actions">
          <button mat-button color="primary" (click)="onOpen(notification)">
            {{ 'common.open' | translate }}
          </button>
          <button mat-button (click)="onDismiss(notification.id)">
            {{ 'desk.notification_dismiss' | translate }}
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin: 16px 0 8px 0;
    }
    .notification-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .notification-card {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border: 1px solid rgba(0, 0, 0, 0.12);
      border-radius: 8px;
      background: #fff;
    }
    .notification-content {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .notification-icon {
      color: rgba(0, 0, 0, 0.54);
    }
    .notification-text {
      font-size: 14px;
    }
    .notification-actions {
      display: flex;
      gap: 4px;
    }
  `],
})
export class VersionNotificationsComponent {
  @Input() notifications: NotificationItem[] = [];
  @Output() dismiss = new EventEmitter<string>();

  onDismiss(id: string): void {
    this.dismiss.emit(id);
  }

  onOpen(notification: NotificationItem): void {
    window.location.href = `/studio/designer/${notification.template_id}`;
  }
}