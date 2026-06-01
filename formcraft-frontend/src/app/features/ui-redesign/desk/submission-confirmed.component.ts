import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

export interface SubmissionConfirmedState {
  referenceNumber: string;
  templateName: string;
  submittedAt: string;
}

@Component({
  selector: 'fc-submission-confirmed',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, TranslateModule],
  templateUrl: './submission-confirmed.component.html',
  styleUrl: './submission-confirmed.component.scss',
})
export class SubmissionConfirmedComponent implements OnInit {
  state: SubmissionConfirmedState | null = null;

  constructor(private router: Router) {}

  ngOnInit(): void {
    const nav = this.router.getCurrentNavigation();
    this.state = (nav?.extras?.state as SubmissionConfirmedState | undefined) ?? null;

    if (!this.state) {
      this.router.navigate(['/ui/desk']);
    }
  }

  backToDesk(): void {
    this.router.navigate(['/ui/desk']);
  }
}
