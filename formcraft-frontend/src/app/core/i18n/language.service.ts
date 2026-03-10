import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { DirectionService, Dir } from './direction.service';

export type Lang = 'ar' | 'en';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private currentLang: Lang = 'ar';

  constructor(
    private translate: TranslateService,
    private directionService: DirectionService
  ) {}

  init(): void {
    this.translate.setDefaultLang('ar');
    this.setLanguage('ar');
  }

  setLanguage(lang: Lang): void {
    this.currentLang = lang;
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
}
