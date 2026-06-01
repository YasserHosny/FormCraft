import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { BreakpointObserver } from '@angular/cdk/layout';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Subject, takeUntil } from 'rxjs';
import { TemplateService } from '../../../core/services/template.service';

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
  imports: [CommonModule, MatIconModule, MatSnackBarModule],
  templateUrl: './designer.component.html',
  styleUrl: './designer.component.scss',
})
export class DesignerComponent implements OnInit, OnDestroy {
  activePropTab = 'props';
  templateId = '';
  templateName = 'طلب فتح حساب جاري للأفراد';
  templateCode = 'AC-001 · v4.2';
  isMobile = false;

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar,
    private templateService: TemplateService,
    private breakpointObserver: BreakpointObserver,
  ) {}

  ngOnInit(): void {
    this.breakpointObserver.observe('(max-width: 599px)')
      .pipe(takeUntil(this.destroy$))
      .subscribe((state) => {
        this.isMobile = state.matches;
      });

    this.templateId = this.route.snapshot.paramMap.get('pageId') || '';
    if (this.templateId) {
      this.templateService.get(this.templateId).subscribe({
        next: (t: any) => {
          this.templateName = t.name || this.templateName;
          this.templateCode = `${t.id?.slice(0, 8) || 'AC-001'} · v${t.version || 1}`;
        },
      });
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

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
