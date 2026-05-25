import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MarketplaceBrowseComponent } from './browse/marketplace-browse.component';
import { MarketplaceDetailComponent } from './detail/marketplace-detail.component';
import { MarketplacePublishComponent } from './publish/marketplace-publish.component';
import { MarketplaceReviewComponent } from './review/marketplace-review.component';

const routes: Routes = [
  { path: '', component: MarketplaceBrowseComponent },
  { path: 'publish', component: MarketplacePublishComponent },
  { path: ':id', component: MarketplaceDetailComponent },
  { path: ':id/review', component: MarketplaceReviewComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class MarketplaceRoutingModule {}
