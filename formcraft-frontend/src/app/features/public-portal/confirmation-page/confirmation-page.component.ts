import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'fc-confirmation-page',
  standalone: false,
  templateUrl: './confirmation-page.component.html',
  styleUrls: ['./confirmation-page.component.scss'],
})
export class ConfirmationPageComponent implements OnInit {
  referenceNumber = '';
  pdfDownloadUrl: string | null = null;
  emailConfirmationStatus: string | null = null;
  language: 'ar' | 'en' = 'ar';
  dir: 'rtl' | 'ltr' = 'rtl';

  constructor(
    private route: ActivatedRoute,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.referenceNumber = params['ref'] || '';
      this.pdfDownloadUrl = params['pdf'] || null;
      this.emailConfirmationStatus = params['emailStatus'] || null;
    });
    this.language = (this.translate.currentLang as 'ar' | 'en') || 'ar';
    this.dir = this.language === 'ar' ? 'rtl' : 'ltr';
  }
}
