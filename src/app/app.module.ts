import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { SignupComponent } from './signup/signup.component';
import { HomeComponent } from './home/home.component';
import { ProfileComponent } from './profile/profile.component';
import { AdminDashboardComponent } from './admin-dashboard/admin-dashboard.component';
import { NavbarComponent } from './navbar/navbar.component';
import { WalletComponent } from './wallet/wallet.component';
import { CartComponent } from './cart/cart.component';
import { WishlistComponent } from './wishlist/wishlist.component';
import { AddressComponent } from './address/address.component';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
import { FooterComponent } from './footer/footer.component';
import { HeaderComponent } from './header/header.component';
import { UserService } from './services/user.service';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';  
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { BookComponent } from './book/book.component';
import { SellerComponent } from './seller/seller.component';
import { DashboardComponent } from './seller/dashboard/dashboard.component';
import { SellerWalletComponent } from './seller/seller-wallet/seller-wallet.component';
import { SellerHeaderComponent } from './seller/seller-header/seller-header.component';
import { ZPageNotFoundComponent } from './z-page-not-found/z-page-not-found.component';
import { SellerProfileComponent } from './seller/seller-profile/seller-profile.component';
import { AdminComponent } from './admin/admin.component';
import { CommonModule } from '@angular/common';
import { CartservicesService } from './services/cartservices.service';
import { AlertComponent } from './alert/alert.component';
import { OrdersComponent } from './orders/orders.component';
import { SellerOrdersComponent } from './seller/seller-orders/seller-orders.component';
import { SearchComponent } from './search/search.component';
import { AdminBookComponent } from './admin-book/admin-book.component';
import { AdminOrderComponent } from './admin-order/admin-order.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    SignupComponent,
    HomeComponent,
    ProfileComponent,
    AdminDashboardComponent,
    NavbarComponent,
    WalletComponent,
    CartComponent,
    WishlistComponent,
    AddressComponent,
    ForgotPasswordComponent,
    FooterComponent,
    HeaderComponent,
    BookComponent,
    SellerComponent,
    DashboardComponent,
    SellerWalletComponent,
    SellerHeaderComponent,
    ZPageNotFoundComponent,
    SellerProfileComponent,
    AdminComponent,
    AlertComponent,
    OrdersComponent,
    SellerOrdersComponent,
    SearchComponent,
    AdminBookComponent,
    AdminOrderComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ReactiveFormsModule,
    FormsModule, 
    HttpClientModule,
    RouterModule,
    CommonModule 
  ],
  
  providers: [UserService,CartservicesService],
  bootstrap: [AppComponent, LoginComponent]
})
export class AppModule { }
