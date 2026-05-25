import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { MarketplaceService } from '../../../core/services/marketplace.service';

@Component({
  selector: 'fc-marketplace-publish',
  standalone: false,
  templateUrl: './marketplace-publish.component.html',
  styleUrls: ['./marketplace-publish.component.scss'],
})
export class MarketplacePublishComponent {
  form = {
    template_id: '',
    description: '',
    tags: '',
    preview_image_urls: '',
    compliance_badges: '',
    price_type: 'free',
    price_amount: null as number | null,
    currency: 'USD',
  };
  saving = false;

  constructor(
    private marketplace: MarketplaceService,
    private router: Router,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {}

  submit(): void {
    this.saving = true;
    this.marketplace
      .publish({
        template_id: this.form.template_id,
        description: this.form.description,
        tags: this.split(this.form.tags),
        preview_image_urls: this.split(this.form.preview_image_urls),
        compliance_badges: this.split(this.form.compliance_badges),
        price_type: this.form.price_type,
        price_amount: this.form.price_type === 'premium' ? this.form.price_amount : null,
        currency: this.form.currency,
      })
      .subscribe({
        next: () => {
          this.saving = false;
          this.snackBar.open(this.translate.instant('marketplace.submitted'), '', {
            duration: 3000,
          });
          this.router.navigate(['/marketplace']);
        },
        error: () => {
          this.saving = false;
          this.snackBar.open(this.translate.instant('marketplace.submitFailed'), '', {
            duration: 3000,
          });
        },
      });
  }

  private split(value: string): string[] {
    return value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
  }
}
