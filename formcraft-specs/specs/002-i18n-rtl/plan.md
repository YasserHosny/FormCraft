# Implementation Plan: Internationalization & RTL Support

**Branch**: `02-i18n-rtl` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement full i18n architecture with Arabic (default) and English, RTL/LTR direction switching, translation-key system via ngx-translate, Angular Material CDK Bidi integration, and mixed-direction input handling.

## Technical Context

**Language/Version**: TypeScript 5.x, Angular (latest LTS)
**Primary Dependencies**: @ngx-translate/core, @ngx-translate/http-loader, @angular/cdk (Bidi module), Angular Material
**Storage**: Translation files in `src/assets/i18n/`, user preference in Supabase profiles table
**Testing**: Jasmine/Karma (unit), Playwright (visual regression)
**Target Platform**: Web (all modern browsers)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First | ✅ Pass | Default language is "ar", default direction is "rtl" |
| VII. Translation-Key | ✅ Pass | All strings via ngx-translate, lint rule for hardcoded strings |
| IX. YAGNI | ✅ Pass | Only ar + en, no additional languages |

## Project Structure

### Frontend (formcraft-frontend)

```text
src/
├── app/
│   ├── core/
│   │   └── i18n/
│   │       ├── i18n.module.ts           # ngx-translate configuration
│   │       ├── direction.service.ts     # Manages dir/lang on <html>, exposes dir$ observable
│   │       └── language.service.ts      # Get/set language, sync with user profile API
│   ├── shared/
│   │   ├── directives/
│   │   │   └── auto-dir.directive.ts    # Applies dir="auto" to input/textarea elements
│   │   └── pipes/
│   │       └── translate-fallback.pipe.ts # Custom pipe with English fallback + warning log
│   └── app.component.ts                 # Subscribes to direction.service, sets <html> attrs
├── assets/
│   └── i18n/
│       ├── ar.json                      # Arabic translations (primary)
│       └── en.json                      # English translations
└── styles/
    ├── _rtl.scss                        # RTL-specific style overrides
    └── _direction-mixins.scss           # SCSS mixins for directional properties
```

### Translation File Structure

```json
{
  "common": {
    "save": "حفظ",
    "cancel": "إلغاء",
    "delete": "حذف",
    "confirm": "تأكيد",
    "loading": "جاري التحميل..."
  },
  "auth": {
    "login": "تسجيل الدخول",
    "logout": "تسجيل الخروج",
    "email": "البريد الإلكتروني",
    "password": "كلمة المرور"
  },
  "templates": {
    "title": "القوالب",
    "create": "إنشاء قالب جديد",
    "actions": {
      "save": "حفظ القالب",
      "publish": "نشر",
      "preview": "معاينة"
    }
  },
  "designer": {
    "title": "استوديو التصميم",
    "elements": {
      "text": "نص",
      "number": "رقم",
      "date": "تاريخ",
      "currency": "عملة",
      "dropdown": "قائمة منسدلة",
      "radio": "اختيار فردي",
      "checkbox": "مربع اختيار",
      "image": "صورة",
      "qr": "رمز QR",
      "barcode": "باركود"
    }
  }
}
```

### Direction Service Architecture

```
User clicks toggle → LanguageService.setLanguage('en')
  → Updates user profile via API (async, non-blocking)
  → DirectionService.setDirection('ltr')
    → Sets document.documentElement.dir = 'ltr'
    → Sets document.documentElement.lang = 'en'
    → Emits dir$ observable → all subscribers re-render
  → TranslateService.use('en')
    → Loads en.json → resolves all keys
```

### SCSS Direction Mixins

```scss
// _direction-mixins.scss
@mixin margin-start($value) {
  [dir="ltr"] & { margin-left: $value; }
  [dir="rtl"] & { margin-right: $value; }
}

@mixin padding-start($value) {
  [dir="ltr"] & { padding-left: $value; }
  [dir="rtl"] & { padding-right: $value; }
}

@mixin float-start {
  [dir="ltr"] & { float: left; }
  [dir="rtl"] & { float: right; }
}
```

## Research Notes

- **ngx-translate** chosen over Angular built-in i18n because Angular i18n requires separate builds per language. ngx-translate supports runtime switching without rebuild.
- **Angular CDK Bidi** provides `Directionality` service and `[dir]` attribute binding. We integrate with it so Angular Material components automatically follow direction.
- **Lint rule**: Custom ESLint rule to detect string literals in Angular templates (excluding known safe patterns like CSS classes and URLs).
- **Number formatting**: Western Arabic numerals (0-9) are used in all locales. Angular's `DecimalPipe` with `locale='en'` ensures this.

## Complexity Tracking

No constitution violations.
