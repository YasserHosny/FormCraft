import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { BreakpointObserver } from '@angular/cdk/layout';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subject, takeUntil } from 'rxjs';
import { TemplateService } from '../../../core/services/template.service';
import { FormDetectionService } from '../../../core/services/form-detection.service';
import { DetectedField, DetectionResponse } from '../../designer/models/detected-field.model';
import { TemplateFeedbackService } from '../../desk/services/template-feedback.service';
import { FeedbackPanelComponent } from '../../designer/feedback-panel/feedback-panel.component';

interface PaletteGroup {
  label: string;
  items: { icon: string; label: string }[];
}

interface DesignerField {
  x: number;
  y: number;
  w: number;
  h: number;
  label?: string;
  kind?: 'input' | 'header' | 'static' | 'check';
  value?: string;
  selected?: boolean;
  ai?: boolean;
  signature?: boolean;
}

interface PropTab {
  key: string;
  label: string;
}

interface ObjectItem {
  icon: string;
  label: string;
  count: number;
}

@Component({
  selector: 'fc-designer',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatSnackBarModule, MatTooltipModule, FeedbackPanelComponent],
  templateUrl: './designer.component.html',
  styleUrl: './designer.component.scss',
})
export class DesignerComponent implements OnInit, OnDestroy {
  @ViewChild('detectFileInput') detectFileInput!: ElementRef<HTMLInputElement>;

  activePropTab = 'props';
  templateId = '';
  templateName = 'طلب فتح حساب جاري للأفراد';
  templateCode = 'AC-001 · v4.2';
  isMobile = false;

  // ── Feedback state ────────────────────────────────────────────────────────
  showFeedbackPanel = false;
  feedbackItems: any[] = [];
  feedbackLoading = false;
  newFeedbackCount = 0;

  // ── AI Detection state ─────────────────────────────────────────────────────
  detectMode: 'import' | 'results' | 'history' | null = null;
  importFile: File | null = null;
  detectLoading = false;
  detections: DetectedField[] = [];
  detectionId = '';
  detectionHistory: DetectionResponse[] = [];
  pendingCount = 0;
  showReplaceConfirm = false;

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar,
    private templateService: TemplateService,
    private detectionService: FormDetectionService,
    private breakpointObserver: BreakpointObserver,
    private feedbackService: TemplateFeedbackService,
  ) {}

  ngOnInit(): void {
    this.breakpointObserver.observe('(max-width: 599px)')
      .pipe(takeUntil(this.destroy$))
      .subscribe((state) => {
        this.isMobile = state.matches;
      });

    this.templateId = this.route.snapshot.paramMap.get('pageId') || '';
    if (this.templateId) {
      this.loadTemplate();
      this.checkPendingCount();
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // ── Navigation / toolbar actions ──────────────────────────────────────────

  goBack(): void {
    this.router.navigate(['/ui/studio/templates']);
  }

  saveDraft(): void {
    this.snackBar.open('تم حفظ المسودة', '', { duration: 3000 });
  }

  submitForReview(): void {
    if (!this.templateId) {
      this.snackBar.open('هذا نموذج تجريبي', '', { duration: 3000 });
      return;
    }
    this.templateService.publish(this.templateId).subscribe({
      next: () => {
        this.snackBar.open('تم إرسال النموذج للمراجعة', '', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open('فشل إرسال النموذج للمراجعة', '', { duration: 3000 });
      },
    });
  }

  preview(): void {
    if (this.templateId) {
      this.router.navigate(['/designer', this.templateId]);
    } else {
      this.snackBar.open('افتح نموذجاً حقيقياً للمعاينة', '', { duration: 3000 });
    }
  }

  // ── Feedback panel ────────────────────────────────────────────────────────

  toggleFeedbackPanel(): void {
    this.showFeedbackPanel = !this.showFeedbackPanel;
    if (this.showFeedbackPanel && this.templateId) {
      this.feedbackLoading = true;
      this.feedbackService.listFeedback(this.templateId).subscribe({
        next: (response) => {
          this.feedbackItems = response.items || [];
          this.newFeedbackCount = this.feedbackItems.filter((f: any) => f.status === 'new').length;
          this.feedbackLoading = false;
        },
        error: () => { this.feedbackLoading = false; },
      });
    }
  }

  closeFeedbackPanel(): void {
    this.showFeedbackPanel = false;
  }

  onAcknowledgeFeedback(feedbackId: string): void {
    this.feedbackService.updateFeedbackStatus(this.templateId, feedbackId, 'acknowledged').subscribe();
  }

  onResolveFeedback(feedbackId: string): void {
    this.feedbackService.updateFeedbackStatus(this.templateId, feedbackId, 'resolved').subscribe();
  }

  // ── AI Detection ──────────────────────────────────────────────────────────

  /**
   * Called on init — quietly fetches the pending detection count so the
   * button badge can render without opening any panel.
   */
  checkPendingCount(): void {
    this.detectionService.listDetections(this.templateId).subscribe({
      next: (list) => {
        this.pendingCount = list.reduce(
          (sum, d) => sum + d.detected_fields.filter((f) => f.status === 'pending').length,
          0,
        );
      },
    });
  }

  /**
   * Main entry point for the "AI Detect" toolbar button.
   * - If already open → close (toggle).
   * - If there are pending detections → ask before replacing.
   * - Otherwise → open the import panel directly.
   */
  openDetect(): void {
    if (this.detectMode !== null || this.showReplaceConfirm) {
      this.closeDetect();
      return;
    }
    if (this.pendingCount > 0) {
      this.showReplaceConfirm = true;
    } else {
      this.detectMode = 'import';
    }
  }

  /** User chose to run a fresh detection, discarding existing pending ones. */
  confirmReplace(): void {
    this.showReplaceConfirm = false;
    this.detectMode = 'import';
    this.importFile = null;
  }

  /** User chose to review the existing pending detections instead. */
  viewExisting(): void {
    this.showReplaceConfirm = false;
    this.detectionService.listDetections(this.templateId).subscribe({
      next: (list) => {
        if (list.length > 0) {
          const latest = list.sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
          )[0];
          this.detectionId = latest.id;
          this.detections = latest.detected_fields.filter((f) => f.status === 'pending');
          this.detectMode = 'results';
        }
      },
    });
  }

  onFileSelected(event: Event): void {
    const el = event.target as HTMLInputElement;
    this.importFile = el.files?.[0] ?? null;
  }

  runDetection(): void {
    if (!this.importFile || !this.templateId) return;
    this.detectLoading = true;
    this.detectionService.importForm(this.templateId, this.importFile).subscribe({
      next: (res) => {
        this.detectionId = res.id;
        this.detections = res.detected_fields;
        this.pendingCount = this.detections.filter((f) => f.status === 'pending').length;
        this.detectMode = 'results';
        this.detectLoading = false;
      },
      error: () => {
        this.snackBar.open('فشل كشف الحقول بالذكاء الاصطناعي', '', { duration: 3000 });
        this.detectLoading = false;
      },
    });
  }

  acceptAllDetections(): void {
    if (!this.templateId || !this.detectionId) return;
    const ids = this.detections.map((_, i) => i);
    this.detectionService.acceptDetections(this.templateId, this.detectionId, ids).subscribe({
      next: (res) => {
        this.snackBar.open(`تم إضافة ${res.created_elements} حقل للنموذج`, '', { duration: 3000 });
        this.detections = [];
        this.pendingCount = 0;
        this.detectMode = null;
        this.loadTemplate();
      },
      error: () => {
        this.snackBar.open('خطأ في قبول الحقول المكتشفة', '', { duration: 3000 });
      },
    });
  }

  rejectAllDetections(): void {
    if (!this.detectionId) {
      this.detectMode = null;
      return;
    }
    this.detectionService.deleteDetection(this.detectionId).subscribe({
      next: () => {
        this.detections = [];
        this.pendingCount = 0;
        this.detectionId = '';
        this.detectMode = null;
      },
    });
  }

  loadHistory(): void {
    this.detectLoading = true;
    this.detectionService.listDetections(this.templateId).subscribe({
      next: (list) => {
        this.detectionHistory = list.sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
        );
        this.detectLoading = false;
        this.detectMode = 'history';
      },
      error: () => {
        this.detectLoading = false;
      },
    });
  }

  viewHistoric(det: DetectionResponse): void {
    this.detectionId = det.id;
    this.detections = det.detected_fields;
    this.detectMode = 'results';
  }

  closeDetect(): void {
    this.detectMode = null;
    this.importFile = null;
    this.showReplaceConfirm = false;
  }

  /** Returns a CSS color for the confidence value (green / orange / red). */
  confidenceColor(conf: number): string {
    if (conf >= 0.8) return 'var(--fc-success, #2E7D32)';
    if (conf >= 0.6) return '#ED6C02';
    return 'var(--fc-error, #C62828)';
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  private loadTemplate(): void {
    this.templateService.get(this.templateId).subscribe({
      next: (t: any) => {
        this.templateName = t.name || this.templateName;
        this.templateCode = `${t.id?.slice(0, 8) || 'AC-001'} · v${t.version || 1}`;
      },
    });
  }

  // ── Static palette / canvas data (prototype) ──────────────────────────────

  propTabs: PropTab[] = [
    { key: 'props', label: 'الخصائص' },
    { key: 'validation', label: 'التحقق' },
    { key: 'logic', label: 'المنطق' },
  ];

  paletteGroups: PaletteGroup[] = [
    {
      label: 'حقول الإدخال',
      items: [
        { icon: 'text_fields', label: 'نص' },
        { icon: '123', label: 'رقم' },
        { icon: 'calendar_today', label: 'تاريخ' },
        { icon: 'arrow_drop_down_circle', label: 'قائمة' },
        { icon: 'check_box', label: 'مربع اختيار' },
        { icon: 'radio_button_checked', label: 'اختيار' },
      ],
    },
    {
      label: 'متقدم',
      items: [
        { icon: 'draw', label: 'توقيع' },
        { icon: 'table_chart', label: 'جدول' },
        { icon: 'qr_code_2', label: 'QR' },
        { icon: 'attach_money', label: 'مبلغ + تفقيط' },
        { icon: 'image', label: 'صورة' },
        { icon: 'upload_file', label: 'إرفاق' },
      ],
    },
    {
      label: 'نصوص ثابتة',
      items: [
        { icon: 'title', label: 'عنوان' },
        { icon: 'notes', label: 'فقرة' },
        { icon: 'horizontal_rule', label: 'خط' },
        { icon: 'space_bar', label: 'فاصل' },
      ],
    },
  ];

  objectItems: ObjectItem[] = [
    { icon: 'folder_open', label: 'الترويسة', count: 3 },
    { icon: 'folder_open', label: 'بيانات العميل', count: 12 },
    { icon: 'folder_open', label: 'تفاصيل الحساب', count: 8 },
    { icon: 'folder_open', label: 'الإقرارات والتوقيع', count: 5 },
  ];

  canvasFields: DesignerField[] = [
    { x: 24, y: 120, w: 268, h: 32, label: 'الاسم الكامل (عربي)', value: 'أحمد محمد العتيبي' },
    { x: 303, y: 120, w: 268, h: 32, label: 'Full Name (EN)', value: 'Ahmed Mohammed Al-Otaibi' },
    { x: 24, y: 164, w: 172, h: 32, label: 'رقم الهوية', value: '2841 9035 1882' },
    { x: 207, y: 164, w: 172, h: 32, label: 'تاريخ الميلاد', value: '1985-03-12' },
    { x: 390, y: 164, w: 181, h: 32, label: 'الجنسية', value: 'إماراتي' },
    { x: 24, y: 208, w: 547, h: 32, label: 'عنوان الإقامة', value: '' },
    { x: 24, y: 292, w: 172, h: 32, label: 'نوع الحساب', value: 'جاري' },
    { x: 207, y: 292, w: 172, h: 32, label: 'العملة', value: 'درهم إماراتي' },
    { x: 390, y: 292, w: 181, h: 32, label: 'مصدر الدخل', value: 'راتب' },
    { x: 24, y: 336, w: 361, h: 42, label: 'الراتب الشهري التقريبي', selected: true, ai: true },
    { x: 396, y: 336, w: 175, h: 42, label: 'تفقيط (تلقائي)', value: 'فقط خمسة عشر ألف درهم' },
    { x: 24, y: 427, w: 547, h: 20, kind: 'check', value: 'أقر بصحة جميع البيانات' },
    { x: 24, y: 453, w: 547, h: 20, kind: 'check', value: 'أوافق على شروط وأحكام فتح الحساب' },
    { x: 24, y: 479, w: 547, h: 20, kind: 'check', value: 'أرغب في إصدار بطاقة الصراف الآلي' },
    { x: 24, y: 520, w: 260, h: 80, label: 'توقيع العميل', signature: true },
    { x: 311, y: 520, w: 260, h: 80, label: 'توقيع الموظف المختص', signature: true },
  ];
}
