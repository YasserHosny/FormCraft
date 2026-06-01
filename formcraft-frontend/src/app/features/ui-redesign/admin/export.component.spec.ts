import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { TranslateFakeLoader, TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { of, throwError } from 'rxjs';

import { ExportComponent } from './export.component';
import { DataExportService } from '../../../core/services/data-export.service';

class MockDataExportService {
  preview = jasmine.createSpy('preview').and.returnValue(of({
    matching_count: 1500,
    estimated_file_size_bytes: 102400,
    can_download: true,
    rejection_reason: null,
    warnings: [],
  }));
  download = jasmine.createSpy('download').and.returnValue(of(new Blob(['test'])));
  listHistory = jasmine.createSpy('listHistory').and.returnValue(of({
    items: [
      { id: '1', dataset: 'submissions', format: 'csv', scope: 'flattened', status: 'completed', matching_count: 1500, created_at: '2026-05-01T10:00:00Z' },
    ],
  }));
}

describe('ExportComponent', () => {
  let component: ExportComponent;
  let fixture: ComponentFixture<ExportComponent>;
  let mockService: MockDataExportService;

  beforeEach(async () => {
    mockService = new MockDataExportService();

    await TestBed.configureTestingModule({
      imports: [
        ExportComponent,
        BrowserAnimationsModule,
        TranslateModule.forRoot({ loader: { provide: TranslateLoader, useClass: TranslateFakeLoader } }),
      ],
      providers: [
        { provide: DataExportService, useValue: mockService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ExportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('loads history on init', () => {
    expect(mockService.listHistory).toHaveBeenCalled();
    expect(component.history.length).toBe(1);
  });

  it('shows empty state when history is empty', () => {
    mockService.listHistory.and.returnValue(of({ items: [] }));
    component.loadHistory();
    fixture.detectChanges();
    expect(component.history.length).toBe(0);
  });

  it('shows preview result after successful preview', () => {
    component.previewExport();
    fixture.detectChanges();
    expect(component.state).toBe('preview_ready');
    expect(component.preview?.matching_count).toBe(1500);
  });

  it('disables download when oversized', () => {
    mockService.preview.and.returnValue(of({
      matching_count: 60000,
      estimated_file_size_bytes: 102400,
      can_download: false,
      rejection_reason: null,
      warnings: [],
    }));
    component.previewExport();
    fixture.detectChanges();
    expect(component.isOversized).toBeTrue();
    expect(component.canDownload).toBeFalse();
  });

  it('triggers download when eligible', () => {
    component.previewExport();
    fixture.detectChanges();
    expect(component.canDownload).toBeTrue();
    component.downloadExport();
    expect(mockService.download).toHaveBeenCalled();
  });

  it('shows error state on preview failure', () => {
    mockService.preview.and.returnValue(throwError(() => new Error('fail')));
    component.previewExport();
    fixture.detectChanges();
    expect(component.state).toBe('preview_error');
  });

  it('shows error state on history failure', () => {
    mockService.listHistory.and.returnValue(throwError(() => new Error('fail')));
    component.loadHistory();
    fixture.detectChanges();
    expect(component.historyError).toBeTrue();
  });
});
