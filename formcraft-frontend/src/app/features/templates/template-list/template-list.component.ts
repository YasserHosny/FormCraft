import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TemplateService } from '../../../core/services/template.service';
import { TemplateCreateDialogComponent } from '../template-create-dialog/template-create-dialog.component';

@Component({
  selector: 'fc-template-list',
  standalone: false,
  templateUrl: './template-list.component.html',
  styleUrls: ['./template-list.component.scss'],
})
export class TemplateListComponent implements OnInit {
  templates: any[] = [];

  constructor(
    private templateService: TemplateService,
    private dialog: MatDialog,
    private router: Router,
    private snackBar: MatSnackBar,
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

  createNewVersion(template: any): void {
    this.templateService.createNewVersion(template.id).subscribe({
      next: (newTemplate: any) => {
        this.snackBar.open(`Version ${newTemplate.version} created`, '', { duration: 3000 });
        this.router.navigate(['/designer', newTemplate.id]);
      },
      error: () => {
        this.snackBar.open('Failed to create new version', '', { duration: 3000 });
      },
    });
  }

  publish(template: any): void {
    this.templateService.publish(template.id).subscribe({
      next: () => {
        this.snackBar.open('Template published', '', { duration: 3000 });
        this.loadTemplates();
      },
      error: () => {
        this.snackBar.open('Failed to publish template', '', { duration: 3000 });
      },
    });
  }

  deleteTemplate(template: any): void {
    this.templateService.delete(template.id).subscribe({
      next: () => {
        this.snackBar.open('Template deleted', '', { duration: 3000 });
        this.loadTemplates();
      },
      error: () => {
        this.snackBar.open('Failed to delete template', '', { duration: 3000 });
      },
    });
  }
}
