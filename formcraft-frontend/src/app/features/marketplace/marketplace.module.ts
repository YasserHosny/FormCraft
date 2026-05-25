import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { MarketplaceRoutingModule } from './marketplace-routing.module';
import { MarketplaceBrowseComponent } from './browse/marketplace-browse.component';
import { MarketplaceDetailComponent } from './detail/marketplace-detail.component';
import { MarketplacePublishComponent } from './publish/marketplace-publish.component';
import { MarketplaceReviewComponent } from './review/marketplace-review.component';

@NgModule({
  declarations: [
    MarketplaceBrowseComponent,
    MarketplaceDetailComponent,
    MarketplacePublishComponent,
    MarketplaceReviewComponent,
  ],
  imports: [SharedModule, MarketplaceRoutingModule],
})
export class MarketplaceModule {}
