import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AvatarComponent } from '../shared/components/avatar.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { TemplateService } from '../../../core/services/template.service';

interface FormField {
  label: string;
  value?: string;
  placeholder?: string;
  filled?: boolean;
  valid?: boolean;
  error?: boolean;
  hint?: string;
  suffix?: string;
  span?: number; // grid column span
}

interface FormSection {
  number: string;
  title: string;
  complete?: boolean;
  fields: FormField[];
  columns: number;
}

interface SideSection {
  number: string;
  label: string;
  state: 'done' | 'active' | 'pending';
  count: string;
}

@Component({
  selector: 'fc-form-filler',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatSnackBarModule, AvatarComponent, StatusChipComponent],
  templateUrl: './form-filler.component.html',
  styleUrl: './form-filler.component.scss',
})
export class FormFillerComponent implements OnInit {
  showCustomerPicker = false;
  templateId = '';
  templateName = 'طلب فتح حساب جاري للأفراد';
  templateCode = 'AC-001 · v4.2';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar,
    private templateService: TemplateService,
  ) {}

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('templateId') || '';
    if (this.templateId) {
      this.templateService.get(this.templateId).subscribe({
        next: (t: any) => {
          this.templateName = t.name || this.templateName;
          this.templateCode = `v${t.version || 1}`;
        },
      });
    }
  }

  goBack(): void {
    this.router.navigate(['/ui/desk']);
  }

  saveDraft(): void {
    this.snackBar.open('تم حفظ المسودة بنجاح', '', { duration: 3000 });
  }

  printPdf(): void {
    if (this.templateId) {
      this.router.navigate(['/desk/fill', this.templateId], { queryParams: { print: true } });
    } else {
      this.snackBar.open('افتح النموذج من مكتب النماذج للطباعة', '', { duration: 3000 });
    }
  }

  submitForm(): void {
    this.snackBar.open('تم إرسال النموذج بنجاح', '', { duration: 3000 });
  }

  sideSections: SideSection[] = [
    { number: '١', label: 'بيانات مقدم الطلب', state: 'done', count: '٧/٧' },
    { number: '٢', label: 'تفاصيل الحساب المطلوب', state: 'active', count: '٧/٨' },
    { number: '٣', label: 'الإقرارات والتوقيع', state: 'pending', count: '٠/٤' },
    { number: '٤', label: 'مرفقات إضافية', state: 'pending', count: '٠/٢' },
  ];

  alerts = [
    { type: 'error', icon: 'error', message: '<b>المسمى الوظيفي</b> حقل مطلوب — لم يُملأ بعد.' },
    { type: 'warn', icon: 'warning', message: 'لم يوقّع العميل بعد. يمكن التوقيع رقمياً أو بعد الطباعة.' },
  ];

  shortcuts = [
    { key: '⌘ + S', label: 'حفظ كمسودة' },
    { key: '⌘ + P', label: 'طباعة' },
    { key: 'Tab', label: 'الحقل التالي' },
    { key: '⌘ + K', label: 'تغيير العميل' },
  ];

  sections: FormSection[] = [
    {
      number: '١', title: 'بيانات مقدم الطلب', complete: true, columns: 2,
      fields: [
        { label: 'الاسم الكامل (عربي)', value: 'فاطمة بنت عبدالله القحطاني', filled: true, valid: true },
        { label: 'Full Name (English)', value: 'Fatima Abdullah Al-Qahtani', filled: true, valid: true },
        { label: 'رقم الهوية الوطنية', value: '2841-9035-1882', filled: true, valid: true, suffix: 'مُتحقق منه' },
        { label: 'تاريخ الميلاد', value: '1992-08-14', filled: true, valid: true },
        { label: 'الجنسية', value: 'إماراتية', filled: true, valid: true },
        { label: 'رقم الجوال', value: '+971 50 423 7188', filled: true, valid: true },
        { label: 'عنوان الإقامة الحالي', value: 'شارع الكرامة، مبنى الواحة، الطابق ٧، شقة ٧٠٤، أبوظبي', filled: true, valid: true, span: 2 },
      ],
    },
    {
      number: '٢', title: 'تفاصيل الحساب المطلوب', columns: 3,
      fields: [
        { label: 'نوع الحساب', value: 'جاري — أفراد', valid: true },
        { label: 'العملة', value: 'درهم إماراتي (AED)', valid: true },
        { label: 'مصدر الدخل', value: 'راتب وظيفي', valid: true },
      ],
    },
  ];

  recentCustomers = ['خالد الدوسري', 'محمد الشمري', 'نورة الزهراني', 'سلمان الغامدي'];

  customerResults = [
    { name: 'فاطمة بنت عبدالله القحطاني', en: 'Fatima Abdullah Al-Qahtani', id: '2841-9035-1882', phone: '+971 50 423 7188', forms: 4, last: 'قبل ١٢ يوماً', color: 'c2', selected: true },
    { name: 'فاطمة بنت محمد العنزي', en: 'Fatima Mohammed Al-Anzi', id: '1956-2284-7401', phone: '+971 50 117 9032', forms: 2, last: 'قبل شهرين', color: 'c5', selected: false },
    { name: 'فاطمة بنت سعد الزهراني', en: 'Fatima Saad Al-Zahrani', id: '3092-8814-2266', phone: '+971 55 802 4413', forms: 7, last: 'قبل ٣ أسابيع', color: 'c3', selected: false },
  ];

  createNewCustomer(): void {
    this.closeCustomerPicker();
    this.router.navigate(['/desk/customers/new']);
  }

  openCustomerPicker(): void {
    this.showCustomerPicker = true;
  }

  closeCustomerPicker(): void {
    this.showCustomerPicker = false;
  }
}
