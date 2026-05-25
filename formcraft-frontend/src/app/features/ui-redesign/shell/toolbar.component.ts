import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';

@Component({
  selector: 'fc-redesign-toolbar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatMenuModule],
  templateUrl: './toolbar.component.html',
  styleUrl: './toolbar.component.scss',
})
export class ToolbarComponent {
  @Input() activeMode: 'studio' | 'desk' | 'admin' = 'studio';
  @Input() unreadCount = 7;
  @Output() notificationClick = new EventEmitter<void>();

  tabs = [
    { key: 'studio', icon: 'brush', label: 'استوديو التصميم', route: '/ui/studio/templates' },
    { key: 'desk', icon: 'assignment', label: 'مكتب النماذج', route: '/ui/desk' },
    { key: 'admin', icon: 'admin_panel_settings', label: 'لوحة الإدارة', route: '/ui/admin/analytics' },
  ];

  user = { name: 'أحمد العتيبي', role: 'مسؤول', initials: 'أع' };
}
