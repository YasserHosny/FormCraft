import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MarketplaceService } from '../../../core/services/marketplace.service';
import { MarketplaceListing } from '../../../shared/models/marketplace.models';

@Component({
  selector: 'fc-marketplace-browse',
  standalone: false,
  templateUrl: './marketplace-browse.component.html',
  styleUrls: ['./marketplace-browse.component.scss'],
})
export class MarketplaceBrowseComponent implements OnInit {
  listings: MarketplaceListing[] = [];
  loading = false;
  total = 0;
  filters = {
    search: '',
    country: '',
    category: '',
    language: '',
    price_type: '',
    sort_by: 'quality_score',
  };

  constructor(
    private marketplace: MarketplaceService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading = true;
    this.marketplace.list({ ...this.filters, page: 1, page_size: 24 }).subscribe({
      next: (response) => {
        this.listings = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  open(listing: MarketplaceListing): void {
    this.router.navigate(['/marketplace', listing.id]);
  }

  clear(): void {
    this.filters = {
      search: '',
      country: '',
      category: '',
      language: '',
      price_type: '',
      sort_by: 'quality_score',
    };
    this.load();
  }
}
