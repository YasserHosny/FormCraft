import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { TemplateService } from '../../../core/services/template.service';
import { TemplateCreateDialogComponent } from '../template-create-dialog/template-create-dialog.component';

@Component({
  selector: 'fc-template-list',
  standalone: false,
  template: `
    <mat-toolbar color="primary">
      <span>{{ 'templates.title' | translate }}</span>
      <span class="spacer"></span>
      <button mat-raised-button (click)="createTemplate()">
        {{ 'templates.create' | translate }}
      </button>
    </mat-toolbar>

    <div class="template-grid">
      <mat-card *ngFor="let template of templates" class="template-card">
        <mat-card-header>
          <mat-card-title>{{ template.name }}</mat-card-title>
          <mat-card-subtitle>{{ template.status }} &middot; v{{ template.version }}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p>{{ template.description }}</p>
        </mat-card-content>
        <mat-card-actions>
          <button mat-button [routerLink]="['/designer', template.id]">
            {{ 'designer.title' | translate }}
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .spacer {
        flex: 1 1 auto;
      }
      .template-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
        padding: 24px;
      }
      .template-card {
        cursor: pointer;
      }
    `,
  ],
})
export class TemplateListComponent implements OnInit {
  templates: any[] = [];

  constructor(
    private templateService: TemplateService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.templateService.list().subscribe({
      next: (response) => {
        this.templates = response.data;
      },
    });
  }

  createTemplate(): void {
    const dialogRef = this.dialog.open(TemplateCreateDialogComponent, {
      width: '520px',
      disableClose: true,
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadTemplates();
      }
    });
  }
}
