import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { DirectionService, Dir } from './direction.service';

export type Lang = 'ar' | 'en';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private readonly storageKey = 'formcraft_language';
  private currentLang: Lang = 'ar';

  constructor(
    private translate: TranslateService,
    private directionService: DirectionService
  ) {}

  init(): void {
    this.translate.setDefaultLang('ar');
    const storedLang = localStorage.getItem(this.storageKey);
    this.setLanguage(this.isSupportedLang(storedLang) ? storedLang : 'ar');
  }

  setLanguage(lang: Lang): void {
    this.currentLang = lang;
    localStorage.setItem(this.storageKey, lang);
    this.translate.use(lang);
    document.documentElement.lang = lang;

    const dir: Dir = lang === 'ar' ? 'rtl' : 'ltr';
    this.directionService.setDirection(dir);
  }

  getLanguage(): Lang {
    return this.currentLang;
  }

  toggleLanguage(): void {
    const next: Lang = this.currentLang === 'ar' ? 'en' : 'ar';
    this.setLanguage(next);
  }

  private isSupportedLang(lang: string | null): lang is Lang {
    return lang === 'ar' || lang === 'en';
  }
}
