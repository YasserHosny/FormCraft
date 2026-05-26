import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { SIDEBAR_DATA } from '../shared/mock-data';

@Component({
  selector: 'fc-redesign-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  @Input() mode: 'studio' | 'desk' | 'admin' = 'studio';

  get groups() {
    return SIDEBAR_DATA[this.mode] || [];
  }
}
