// Mock data for UI Redesign prototype

export interface Template {
  id: number;
  name: string;
  code: string;
  status: string;
  version: string;
  dept: string;
  updated: string;
  by: string;
  color: string;
  submissions: number;
  pages: number;
  fields: number;
}

export interface Customer {
  name: string;
  en: string;
  idType: string;
  id: string;
  phone: string;
  email: string;
  branch: string;
  status: string;
  forms: number;
  last: string;
  color: string;
  tag?: string;
  dup?: boolean;
}

export interface Notification {
  kind: string;
  icon: string;
  color: string;
  bg: string;
  title: string;
  body: string;
  time: string;
  unread: boolean;
  action?: string;
}

export const TEMPLATES: Template[] = [
  { id: 1, name: 'طلب فتح حساب جاري للأفراد', code: 'AC-001', status: 'published', version: 'v4.2', dept: 'الحسابات الجارية', updated: 'قبل ساعتين', by: 'فاطمة', color: 'c2', submissions: 1284, pages: 2, fields: 38 },
  { id: 2, name: 'نموذج تحديث بيانات العميل (KYC)', code: 'KYC-018', status: 'published', version: 'v2.0', dept: 'الالتزام', updated: 'أمس 14:22', by: 'خالد', color: 'c1', submissions: 942, pages: 3, fields: 52 },
  { id: 3, name: 'طلب إصدار بطاقة الصراف الآلي', code: 'CRD-007', status: 'in-review', version: 'v1.5', dept: 'الخدمات الإلكترونية', updated: 'قبل 30 دقيقة', by: 'نورة', color: 'c3', submissions: 0, pages: 1, fields: 24 },
  { id: 4, name: 'طلب قرض شخصي', code: 'LN-002', status: 'approved', version: 'v3.1', dept: 'القروض', updated: 'قبل 4 ساعات', by: 'محمد', color: 'c4', submissions: 612, pages: 4, fields: 67 },
  { id: 5, name: 'طلب إصدار خطاب ضمان', code: 'LG-011', status: 'draft', version: 'v0.3', dept: 'الخدمات المؤسسية', updated: 'قبل 5 أيام', by: 'ريم', color: 'c5', submissions: 0, pages: 2, fields: 41 },
  { id: 6, name: 'إقرار صاحب الحق الفعلي', code: 'BO-004', status: 'published', version: 'v1.8', dept: 'الالتزام', updated: 'قبل أسبوع', by: 'سلمان', color: 'c6', submissions: 287, pages: 1, fields: 19 },
  { id: 7, name: 'طلب تحويل خارجي', code: 'TR-022', status: 'published', version: 'v2.3', dept: 'الحوالات', updated: 'قبل يومين', by: 'هدى', color: 'c2', submissions: 1837, pages: 1, fields: 28 },
  { id: 8, name: 'طلب إصدار دفتر شيكات', code: 'CHQ-009', status: 'draft', version: 'v0.1', dept: 'الحسابات الجارية', updated: 'قبل 3 أيام', by: 'فاطمة', color: 'c2', submissions: 0, pages: 1, fields: 14 },
  { id: 9, name: 'نموذج تفويض سحب راتب', code: 'PR-031', status: 'archived', version: 'v1.2', dept: 'الموارد البشرية', updated: 'قبل شهرين', by: 'علي', color: 'c4', submissions: 92, pages: 1, fields: 21 },
  { id: 10, name: 'استمارة فتح وديعة استثمارية', code: 'DEP-014', status: 'in-review', version: 'v2.1', dept: 'الاستثمار', updated: 'قبل ساعة', by: 'منى', color: 'c5', submissions: 0, pages: 2, fields: 33 },
  { id: 11, name: 'طلب إغلاق حساب', code: 'AC-019', status: 'published', version: 'v1.0', dept: 'الحسابات الجارية', updated: 'الأسبوع الماضي', by: 'فاطمة', color: 'c2', submissions: 412, pages: 1, fields: 12 },
  { id: 12, name: 'تعبئة معلومات الشركات', code: 'CO-006', status: 'rejected', version: 'v0.4', dept: 'الخدمات المؤسسية', updated: 'قبل ساعة', by: 'ريم', color: 'c5', submissions: 0, pages: 3, fields: 58 },
];

export const CUSTOMERS: Customer[] = [
  { name: 'فاطمة بنت عبدالله القحطاني', en: 'Fatima Abdullah Al-Qahtani', idType: 'هوية وطنية', id: '2841-9035-1882', phone: '+971 50 423 7188', email: 'f.qahtani@example.ae', branch: 'أبوظبي الرئيسي', status: 'active', forms: 12, last: 'قبل ١٢ يوماً', color: 'c2', tag: 'متميز' },
  { name: 'خالد بن سعد الدوسري', en: 'Khalid Saad Al-Dosari', idType: 'هوية وطنية', id: '1023-4471-8829', phone: '+971 55 901 4422', email: 'k.dosari@example.ae', branch: 'دبي - الخليج التجاري', status: 'active', forms: 8, last: 'أمس', color: 'c1' },
  { name: 'نورة بنت إبراهيم الزهراني', en: 'Noura Ibrahim Al-Zahrani', idType: 'إقامة', id: '7849-2210-4458', phone: '+971 52 113 7702', email: 'noura.zahrani@example.ae', branch: 'الشارقة - الممزر', status: 'active', forms: 4, last: 'قبل ٣ أيام', color: 'c3' },
  { name: 'محمد بن علي الشمري', en: 'Mohammed Ali Al-Shammari', idType: 'هوية وطنية', id: '5092-8814-2266', phone: '+971 50 880 1133', email: 'm.shammari@example.ae', branch: 'أبوظبي الرئيسي', status: 'active', forms: 19, last: 'اليوم ١٠:٤٢', color: 'c4', tag: 'تكرار محتمل' },
  { name: 'محمد علي الشمّري', en: 'Mohammad A. Al-Shammari', idType: 'هوية وطنية', id: '5092-8814-2266', phone: '+971 50 880 1133', email: '—', branch: 'دبي - الخليج التجاري', status: 'active', forms: 3, last: 'قبل ٣ أشهر', color: 'c4', dup: true },
  { name: 'ريم بنت فهد العنزي', en: 'Reem Fahd Al-Anzi', idType: 'هوية وطنية', id: '4180-2245-0073', phone: '+971 54 660 8821', email: 'reem.anzi@example.ae', branch: 'العين - الجيمي', status: 'active', forms: 6, last: 'قبل ٤٥ دقيقة', color: 'c5' },
  { name: 'سلمان بن أحمد الغامدي', en: 'Salman Ahmed Al-Ghamdi', idType: 'إقامة', id: '8923-1145-7702', phone: '+971 56 220 3318', email: 'salman.g@example.ae', branch: 'أبوظبي الرئيسي', status: 'active', forms: 22, last: 'قبل ساعتين', color: 'c6' },
  { name: 'هدى بنت محمد الحربي', en: 'Huda Mohammed Al-Harbi', idType: 'هوية وطنية', id: '2274-0918-3346', phone: '+971 50 778 9912', email: 'huda.harbi@example.ae', branch: 'دبي - الخليج التجاري', status: 'inactive', forms: 1, last: 'قبل ٧ أشهر', color: 'c3' },
  { name: 'عبدالعزيز بن خالد المالكي', en: 'Abdulaziz Khalid Al-Maliki', idType: 'هوية وطنية', id: '1882-4423-9051', phone: '+971 52 008 4451', email: 'a.maliki@example.ae', branch: 'الشارقة - الممزر', status: 'active', forms: 15, last: 'قبل يومين', color: 'c1' },
  { name: 'لمياء بنت سعود العتيبي', en: 'Lamia Saud Al-Otaibi', idType: 'هوية وطنية', id: '6712-3308-1129', phone: '+971 50 992 1043', email: 'lamia.o@example.ae', branch: 'العين - الجيمي', status: 'active', forms: 9, last: 'قبل ٥ أيام', color: 'c5' },
  { name: 'شركة الفجر للمقاولات', en: 'Al-Fajr Contracting LLC', idType: 'سجل تجاري', id: 'CR-1102-4471', phone: '+971 2 612 8800', email: 'finance@alfajr.ae', branch: 'أبوظبي الرئيسي', status: 'active', forms: 31, last: 'اليوم ٠٩:١٥', color: 'c4', tag: 'مؤسسي' },
];

export const NOTIFICATIONS: Notification[] = [
  { kind: 'review_request', icon: 'rate_review', color: '#1565C0', bg: '#E3F2FD', title: 'طلب مراجعة قالب جديد', body: 'أرسلت <b>نورة الزهراني</b> القالب <b>"طلب إصدار بطاقة الصراف (v1.5)"</b> للمراجعة', time: 'قبل ٤ دقائق', unread: true, action: 'مراجعة' },
  { kind: 'approved', icon: 'verified', color: '#2E7D32', bg: '#E8F5E9', title: 'تمت الموافقة على قالبك', body: 'وافق <b>خالد الدوسري</b> على <b>"تحويل خارجي (v2.3)"</b> — جاهز للنشر', time: 'قبل ٢١ دقيقة', unread: true, action: 'نشر' },
  { kind: 'feedback', icon: 'comment', color: '#FFA000', bg: '#FFF3E0', title: 'ملاحظات مراجعة جديدة', body: 'أضافت <b>فاطمة القحطاني</b> ٣ ملاحظات على <b>"طلب قرض شخصي (v3.1)"</b>', time: 'قبل ساعة', unread: true, action: 'عرض' },
  { kind: 'rejected', icon: 'cancel', color: '#C62828', bg: '#FDECEA', title: 'تم رفض قالبك', body: 'رفض <b>سلمان الغامدي</b> <b>"معلومات الشركات (v0.4)"</b> — يحتاج تعديلات', time: 'قبل ٣ ساعات', unread: true, action: 'تعديل' },
  { kind: 'published', icon: 'public', color: '#3F51B5', bg: '#EEF0FA', title: 'تم نشر القالب', body: 'أصبح <b>"طلب إغلاق حساب (v1.0)"</b> متاحاً لجميع موظفي الخدمة', time: 'أمس ١٦:٤٢', unread: true },
  { kind: 'mention', icon: 'alternate_email', color: '#6A1B9A', bg: '#F3E5F5', title: 'تم الإشارة إليك', body: '<b>محمد الشمري</b> أشار إليك في تعليق على <b>"تحديث بيانات KYC"</b>', time: 'أمس ١٤:١٨', unread: true },
  { kind: 'merge', icon: 'merge_type', color: '#00897B', bg: '#E0F2F1', title: 'تم دمج ملفي عميل', body: 'دمج <b>أحمد العتيبي</b> ملفين مكررين للعميل <b>محمد بن علي الشمري</b>', time: 'قبل يومين', unread: false },
  { kind: 'system', icon: 'system_update', color: '#797E8E', bg: '#F0F1F5', title: 'تحديث النظام v3.2', body: 'إضافات جديدة: تحقق ذكي بالـAI، تحسينات على لوحة التحليلات، دعم تصدير Excel', time: 'قبل ٣ أيام', unread: false },
];

export const SIDEBAR_DATA = {
  studio: [
    { label: 'استوديو التصميم', items: [
      { icon: 'dashboard', label: 'نظرة عامة', route: '/ui/studio' },
      { icon: 'description', label: 'النماذج', route: '/ui/studio/templates', count: 47 },
      { icon: 'history', label: 'سجل الإصدارات', route: '' },
      { icon: 'folder_special', label: 'القوالب الجاهزة', route: '', count: 12 },
      { icon: 'palette', label: 'مكوّنات قابلة للاستخدام', route: '' },
    ]},
    { label: 'الذكاء الاصطناعي', items: [
      { icon: 'auto_awesome', label: 'اقتراحات الحقول', route: '' },
      { icon: 'fact_check', label: 'فحص جودة النموذج', route: '' },
    ]},
  ],
  desk: [
    { label: 'مكتب النماذج', items: [
      { icon: 'home', label: 'الرئيسية', route: '/ui/desk' },
      { icon: 'edit_document', label: 'تعبئة نموذج جديد', route: '' },
      { icon: 'inbox', label: 'الواردات', route: '', count: 38 },
      { icon: 'pending_actions', label: 'المسوّدات', route: '', count: 6 },
      { icon: 'history', label: 'سجل المعاملات', route: '' },
    ]},
    { label: 'العملاء', items: [
      { icon: 'groups', label: 'دليل العملاء', route: '/ui/desk/customers', count: 2841 },
      { icon: 'person_add', label: 'إضافة عميل', route: '' },
      { icon: 'merge_type', label: 'دمج التكرارات', route: '', count: 4 },
    ]},
  ],
  admin: [
    { label: 'لوحة الإدارة', items: [
      { icon: 'dashboard', label: 'نظرة عامة', route: '/ui/admin' },
      { icon: 'analytics', label: 'التحليلات والتقارير', route: '/ui/admin/analytics' },
      { icon: 'rule', label: 'قائمة المراجعة', route: '', count: 12 },
      { icon: 'history_edu', label: 'سجل النشاط', route: '' },
    ]},
    { label: 'المؤسسة', items: [
      { icon: 'people', label: 'المستخدمون', route: '', count: 184 },
      { icon: 'account_tree', label: 'الإدارات والفروع', route: '' },
      { icon: 'business', label: 'إعدادات المؤسسة', route: '' },
      { icon: 'list_alt', label: 'البيانات المرجعية', route: '' },
      { icon: 'print', label: 'ملفات تعريف الطابعات', route: '' },
    ]},
  ],
};

export const STATUS_LABELS: Record<string, string> = {
  draft: 'مسوّدة',
  'in-review': 'قيد المراجعة',
  approved: 'معتمد',
  published: 'منشور',
  archived: 'مؤرشف',
  rejected: 'مرفوض',
  active: 'نشط',
  inactive: 'موقوف',
};
