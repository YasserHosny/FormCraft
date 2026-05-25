import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { MarketplaceService } from '../../../core/services/marketplace.service';

@Component({
  selector: 'fc-marketplace-review',
  standalone: false,
  templateUrl: './marketplace-review.component.html',
  styleUrls: ['./marketplace-review.component.scss'],
})
export class MarketplaceReviewComponent {
  listingId = '';
  form = {
    import_id: '',
    rating: 5,
    review_text: '',
  };
  saving = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private marketplace: MarketplaceService,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {
    this.listingId = this.route.snapshot.paramMap.get('id') || '';
  }

  submit(): void {
    if (!this.listingId) return;
    this.saving = true;
    this.marketplace.review(this.listingId, this.form).subscribe({
      next: () => {
        this.saving = false;
        this.snackBar.open(this.translate.instant('marketplace.reviewSaved'), '', {
          duration: 3000,
        });
        this.router.navigate(['/marketplace', this.listingId]);
      },
      error: () => {
        this.saving = false;
        this.snackBar.open(this.translate.instant('marketplace.reviewFailed'), '', {
          duration: 3000,
        });
      },
    });
  }
}
