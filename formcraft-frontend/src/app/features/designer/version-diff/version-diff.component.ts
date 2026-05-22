import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatListModule } from '@angular/material/list';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-version-diff',
  standalone: true,
  imports: [
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatTableModule,
    MatListModule,
    TranslateModule,
  ],
  templateUrl: './version-diff.component.html',
  styleUrls: ['./version-diff.component.scss'],
})
export class VersionDiffComponent {
  @Input() diff: any = null;

  get summaryText(): string {
    if (!this.diff?.summary) return '';
    const s = this.diff.summary;
    return `${s.elements_added} added, ${s.elements_removed} removed, ${s.elements_modified} modified`;
  }

  get addedElements(): any[] {
    return this.diff?.changes?.added || [];
  }

  get removedElements(): any[] {
    return this.diff?.changes?.removed || [];
  }

  get modifiedElements(): any[] {
    return this.diff?.changes?.modified || [];
  }
}