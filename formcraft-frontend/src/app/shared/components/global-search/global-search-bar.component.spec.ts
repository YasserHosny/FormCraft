import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { TranslateFakeLoader, TranslateLoader, TranslateModule, TranslateService } from '@ngx-translate/core';
import { of } from 'rxjs';

import { SearchService } from '../../../core/services/search.service';
import { GlobalSearchBarComponent } from './global-search-bar.component';

describe('GlobalSearchBarComponent', () => {
  let fixture: ComponentFixture<GlobalSearchBarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        GlobalSearchBarComponent,
        TranslateModule.forRoot({
          loader: { provide: TranslateLoader, useClass: TranslateFakeLoader },
        }),
      ],
      providers: [
        {
          provide: SearchService,
          useValue: {
            getRecentSearches: () => [],
            createSearchObservable$: () => of({ results: [] }),
          },
        },
        { provide: Router, useValue: { navigate: jasmine.createSpy('navigate') } },
      ],
    }).compileComponents();

    const translate = TestBed.inject(TranslateService);
    translate.setTranslation('ar', {
      search: {
        placeholder: 'ابحث في النماذج والتسليمات والعملاء...',
        aria_label: 'البحث العام',
        results_label: 'نتائج البحث',
      },
    });
    translate.use('ar');

    fixture = TestBed.createComponent(GlobalSearchBarComponent);
    fixture.detectChanges();
  });

  it('renders translated search copy as the native input placeholder', () => {
    const input: HTMLInputElement = fixture.nativeElement.querySelector('input');
    const label: HTMLElement | null = fixture.nativeElement.querySelector('mat-label');

    expect(input.getAttribute('placeholder')).toBe('ابحث في النماذج والتسليمات والعملاء...');
    expect(label).toBeNull();
  });
});
