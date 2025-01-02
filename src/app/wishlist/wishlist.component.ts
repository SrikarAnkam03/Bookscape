import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { WishlistService } from '../services/wishlistservices.service';
import { CartservicesService } from '../services/cartservices.service';

@Component({
  selector: 'app-wishlist',
  templateUrl: './wishlist.component.html',
  styleUrls: ['./wishlist.component.css']
})
export class WishlistComponent implements OnInit {
  wishlistItems: any[] = [];
  wishlistId: string | null = null;
  userId: string | null = localStorage.getItem('userId');
  errorMessage: string = '';
  alertMessage: string | null = null;  
  quantity: number = 1;

  constructor(
    private router: Router,
    private wishlistService: WishlistService,
    private cartService: CartservicesService
  ) {}

  ngOnInit(): void {
    this.fetchWishlistItems();
  }

  fetchWishlistItems(): void {
    const wishlistId = localStorage.getItem('wishlist_id');
    if (wishlistId) {
      this.wishlistService.getWishlistItems(wishlistId).subscribe(
        response => {
          if (response.wishlist_items) {
            this.wishlistItems = response.wishlist_items;
          } else {
            console.error('No wishlist items found:', response.message);
          }
        },
        error => {
          console.error('Error fetching wishlist items:', error);
        }
      );
    } else {
      console.error('Wishlist ID not found in localStorage.');
    }
  }

  addToCart(book: any): void {
    const cartItem = {
      cart_id: localStorage.getItem('cart_id'),
      bookId: book.book_id,
      quantity: this.quantity
    };
    this.alertMessage = null;


    this.cartService.addCartItem(cartItem).subscribe(
      (response) => {
        this.alertMessage = response.message;
        console.log('Item added to cart:', response);
      },
      (error) => {
        console.error('Error adding item to cart:', error);
      }
    );
  }

  removeFromWishlist(bookId: string): void {
    this.alertMessage = null;

    this.wishlistService.removeFromWishlist(bookId).subscribe(
      response => {
        this.alertMessage = response.message;
        console.log('Book removed from wishlist:');
        this.wishlistItems = this.wishlistItems.filter(item => item.book_id !== bookId);
      },
      error => {
        console.error('Error removing book from wishlist:', error);
      }
    );
  }

  viewBookDetails(bookTitle: string): void {
    this.router.navigate(['/book', bookTitle]);
  }

  getStars(rating: number): { filled: boolean }[] {
    const stars = [];
    const maxStars = 5;

    for (let i = 1; i <= maxStars; i++) {
      stars.push({ filled: i <= rating });
    }

    return stars;
  }
}
