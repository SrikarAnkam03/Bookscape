import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CartservicesService } from '../services/cartservices.service';
import { WalletService } from '../services/walletservices.service';
import { OrderService } from '../services/order.service';

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit {
  apiUrlAddress: string = `http://127.0.0.1:5000/address`;
  selectedAddressId: string | null = null;
  errorMessage: string | null = null;
  userWalletBalance: number = 0;
  isModalOpen: boolean = false;
  userId: string | null = '';
  quantity: number = 1;
  addresses: any[] = [];
  cartItems: any[] = [];
  alertMessage: string | null = null;



  constructor(
    private http: HttpClient,
    private cartService: CartservicesService, 
    private walletService: WalletService,
    private orderService: OrderService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('userId') || '';
    const cartId = localStorage.getItem('cart_id');
    
    if (this.userId && cartId) {
      this.getCartItems();
    } else {
      this.errorMessage = 'User ID or Cart ID not found. Please log in again.';
    }
  }

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.warn('Authorization token is missing');
      return new HttpHeaders();
    }
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  increaseQuantity(cartItem: any): void {
    if (cartItem.quantity < cartItem.stock) {
      cartItem.quantity++;
      this.updateCartItemQuantity(cartItem);
    } else {
      alert(`Only ${cartItem.stock} items left in stock`);
    }
  }  
  
  decreaseQuantity(cartItem: any): void {
    if (cartItem.quantity > 1) {
      cartItem.quantity--;
      this.updateCartItemQuantity(cartItem); 
    }
  }

  updateCartItemQuantity(cartItem: any): void {
    this.cartService.updateCartItemQuantity(cartItem.cart_item_id, cartItem.quantity).subscribe(
      response => {
        console.log('Quantity updated successfully:', response);
        this.getCartItems();
      },
      error => {
        console.error('Error updating quantity:', error);
      }
    );
  }
  
  confirmOrder(): void {
    if (this.selectedAddressId) {
      this.orderService.placeOrder(this.selectedAddressId).subscribe(
        response => {
          this.getCartItems();
          this.getUserWalletBalance();
          alert('Order placed successfully!');
          console.log(response.message)
          this.router.navigate(['/orders']);
        },
        error => {
          const errorMessage = error.error?.message || 'Error placing order. Please try again later.';
          alert(errorMessage);
          console.error('Error placing order:', errorMessage);
        }
      );
    } else {
      alert('Please select an address to place your order.');
    }
    this.closeModal();
  }

  fetchAddresses(): void {
    const headers = this.getHeaders();

    this.http.get<any[]>(`${this.apiUrlAddress}?user_id=${this.userId}`, {headers}).subscribe(
      (response) => {
        this.addresses = response;
        if (this.addresses.length > 0) {
          this.selectedAddressId = this.addresses[0].address_id;
        }
      },
      (error) => {
        console.error('Error fetching addresses:', error);
      }
    );
  }
  
  checkForNewAddress(): void {
    if (this.selectedAddressId === 'new') {
      this.router.navigate(['/address']);
      this.selectedAddressId = this.addresses.length > 0 ? this.addresses[0].address_id : null;
    }
  }
  
  openAddressFormModal(): void {
    this.isModalOpen = true;
  }

  getCartItems(): void {
    const cartId = localStorage.getItem('cart_id');
    if (cartId) {
      this.cartService.getCartItems(cartId).subscribe(
        (response) => {
          if (response.cart_items) {
            this.cartItems = response.cart_items; 
          } else {
            this.cartItems = []; 
          }
        },
        (error) => {
          this.errorMessage = 'Error fetching cart items.';
          console.error(this.errorMessage);
        }
      );
    } else {
      this.errorMessage = 'Cart ID not found.';
    }
  }

  removeFromCart(cartItemId: string): void {
    this.cartService.removeCartItem(cartItemId).subscribe(
      (response) => {
        console.log('Item removed successfully:', response);
        this.alertMessage = response.message; 
        this.getCartItems(); 
      },
      (error) => {
        console.error('Error removing item:', error);
      }
    );
  }

  viewBookDetails(bookTitle: string): void {
    this.router.navigate(['/book', bookTitle]);
  }

  getTotalPrice(): number {
    return this.cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  }

  proceedToCheckout(): void {
    this.openModal();
  }

  getUserWalletBalance(): void {
    this.walletService.getBalance().subscribe(
      (response) => {
        this.userWalletBalance = response.balance;
      },
      (error) => {
        console.error('Error fetching wallet balance:', error);
      }
    );
  }
  
  hasUnavailableItems(): boolean {
    return this.cartItems.some(item => item.display === false || item.stock === 0);
  }

  openModal(): void {
    this.fetchAddresses();
    this.isModalOpen = true;
  }
  
  closeModal(): void {
    this.isModalOpen = false;
  }
}
