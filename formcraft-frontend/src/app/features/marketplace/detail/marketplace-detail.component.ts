import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { MarketplaceService } from '../../../core/services/marketplace.service';
import { MarketplaceListingDetail } from '../../../shared/models/marketplace.models';

@Component({
  selector: 'fc-marketplace-detail',
  standalone: false,
  templateUrl: './marketplace-detail.component.html',
  styleUrls: ['./marketplace-detail.component.scss'],
})
export class MarketplaceDetailComponent implements OnInit {
  listing?: MarketplaceListingDetail;
  loading = false;
  importing = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private marketplace: MarketplaceService,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loading = true;
      this.marketplace.get(id).subscribe({
        next: (listing) => {
          this.listing = listing;
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        },
      });
    }
  }

  useTemplate(): void {
    if (!this.listing) return;
    if (this.listing.price_type === 'premium') {
      this.marketplace.purchase(this.listing.id).subscribe({
        next: () => this.importListing(),
        error: () =>
          this.snackBar.open(this.translate.instant('marketplace.purchaseFailed'), '', {
            duration: 3000,
          }),
      });
      return;
    }
    this.importListing();
  }

  importListing(): void {
    if (!this.listing) return;
    this.importing = true;
    this.marketplace
      .importListing(this.listing.id, {
        draft_name: `${this.listing.name} Marketplace`,
        accept_disabled_dependencies: true,
      })
      .subscribe({
        next: (result) => {
          this.importing = false;
          this.snackBar.open(this.translate.instant('marketplace.imported'), '', {
            duration: 3000,
          });
          this.router.navigate(['/designer', result.template_id]);
        },
        error: () => {
          this.importing = false;
          this.snackBar.open(this.translate.instant('marketplace.importFailed'), '', {
            duration: 3000,
          });
        },
      });
  }
}
