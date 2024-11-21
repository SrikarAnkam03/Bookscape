import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { SignupComponent } from './signup/signup.component';
import { ProfileComponent } from './profile/profile.component';
import { AddressComponent } from './address/address.component';
import { CartComponent } from './cart/cart.component';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
import { WalletComponent } from './wallet/wallet.component';
import { WishlistComponent } from './wishlist/wishlist.component';
import { BookComponent } from './book/book.component';
import { SellerComponent } from './seller/seller.component';
import { DashboardComponent } from './seller/dashboard/dashboard.component';
import { SellerWalletComponent } from './seller/seller-wallet/seller-wallet.component';
import { RoleGuard } from './auth.guard';
import { ZPageNotFoundComponent } from './z-page-not-found/z-page-not-found.component';
import { SellerProfileComponent } from './seller/seller-profile/seller-profile.component';
import { OrdersComponent } from './orders/orders.component';
import { SellerOrdersComponent } from './seller/seller-orders/seller-orders.component';
import { SearchComponent } from './search/search.component';
import { AdminComponent } from './admin/admin.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { AdminBookComponent } from './admin-book/admin-book.component';
import { AdminOrderComponent } from './admin-order/admin-order.component';

const routes: Routes = [
  {
    path: '',
    component: LoginComponent,
  },
  {
    path: "login",
    component: LoginComponent,
  },
  {
    path: "signup", 
    component: SignupComponent,
  },
  {
    path: "forgotPassword",
    component: ForgotPasswordComponent,
  },
  {
    path: "home",
    component: HomeComponent,
    canActivate: [RoleGuard], 
    data: {role: 'User'}
  },
  {
    path: "search",
    component: SearchComponent,
    canActivate: [RoleGuard], 
    data: {role: 'User'}
  },
  {
    path: "profile",
    component: ProfileComponent,
    canActivate: [RoleGuard], 
    data: {role: 'User'}
  },
  {
    path: "wallet",
    component: WalletComponent,
    canActivate: [RoleGuard],
    data: {role: 'User'}
  },
  {
    path: "cart",
    component: CartComponent,
    canActivate: [RoleGuard],
    data: {role: 'User'}
  },
  {
    path: "wishlist",
    component: WishlistComponent,
    canActivate: [RoleGuard],
    data: {role: 'User'}
  },
  {
    path: "orders",
    component: OrdersComponent,
    canActivate: [RoleGuard],
    data: {role: 'User'}
  },
  {
    path: "address",
    component: AddressComponent,
    canActivate: [RoleGuard],
    data: {role: 'User'}
  },
  {
    path: "admin",
    component: AdminComponent,
    canActivate: [RoleGuard],
    data: {role: 'Admin'}
  },
  {
    path: "admin/:username",
    component: AdminDashboardComponent,
    canActivate: [RoleGuard],
    data: {role: 'Admin'}
  },
  {
    path: "adminBook/:title",
    component: AdminBookComponent,
    canActivate: [RoleGuard],
    data: {role: 'Admin'}
  },
  {
    path: "order/:order_id",
    component: AdminOrderComponent,
    canActivate: [RoleGuard],
    data: {role: 'Admin'}
  },
  {
    path: 'book/:title',
    component: BookComponent,
    canActivate: [RoleGuard],
    data: {role: 'User'}
  },
  {
    path: 'seller',
    component: SellerComponent,
  },
  {
    path: 'sellerprofile',
    component: SellerProfileComponent,
    canActivate: [RoleGuard],
    data: {role: 'Seller'}
  },
  {
    path: 'sellerWallet',
    component: SellerWalletComponent,
    canActivate: [RoleGuard],
    data: {role: 'Seller'}
  },
  {
    path: "sellerOrders",
    component: SellerOrdersComponent,
    canActivate: [RoleGuard],
    data: {role: 'Seller'}
  },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [RoleGuard],
    data: {role: 'Seller'}
  },
  {
    path: "**",
    component: ZPageNotFoundComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
