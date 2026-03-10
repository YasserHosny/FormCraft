import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
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
