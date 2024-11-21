import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { UserService } from '../services/user.service';
import { WalletService } from '../services/walletservices.service';
import { CartservicesService } from '../services/cartservices.service';
import { WishlistService } from '../services/wishlistservices.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private walletService: WalletService,
    private cartService: CartservicesService,
    private wishlistService: WishlistService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(15)]]
    });
  }

  onSubmit() {
    this.loginForm.markAllAsTouched();
  
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;
  
      this.userService.login(email, password).subscribe(
        (response: any) => {
          if (response.message === 'Login successful') {
            
            // Wallet creation logic
            this.walletService.createWallet(response.userId).subscribe(
              walletResponse => {
                if (walletResponse.wallet_id) {
                  localStorage.setItem('wallet_id', walletResponse.wallet_id);
                } else {
                  console.log('Wallet:', walletResponse.message);
                }
              },
              error => console.error('Error creating wallet:', error)
            );
  
            // Cart creation logic
            this.cartService.createCart(response.userId).subscribe(
              cartResponse => {
                if (cartResponse.cart_id) {
                  localStorage.setItem('cart_id', cartResponse.cart_id);
                } else {
                  console.log('Cart:', cartResponse.message);
                }
              },
              error => console.error('Error creating cart:', error)
            );
  
            // Wishlist creation logic
            this.wishlistService.createWishlist(response.userId).subscribe(
              wishlistResponse => {
                if (wishlistResponse.wishlist_id) {
                  localStorage.setItem('wishlist_id', wishlistResponse.wishlist_id);
                } else {
                  console.log('Wishlist:', wishlistResponse.message);
                }
              },
              error => console.error('Error creating wishlist:', error)
            );
  
            if (response.role_name === 'Admin') {
              this.router.navigate(['/admin']);
            } else if (response.role_name === 'User') {
              this.router.navigate(['/home']);
            } else if (response.role_name === 'Seller') {
              this.router.navigate(['/dashboard']);
            }
          } else {
            this.errorMessage = response.message;
          }
        },
        error => {
          if (error?.status === 400 || error?.status === 401 || error?.status === 403 || error?.status === 404 ) {
            this.errorMessage = error.error.message;
          } else {
            this.errorMessage = 'An error occurred during login. Please try again.';
          }
        }
      );
    } else {
      this.errorMessage = 'Please fill out all required fields correctly.';
    }
  }
  
}
