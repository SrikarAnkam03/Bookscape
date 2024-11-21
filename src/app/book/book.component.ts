import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BookservicesService } from '../services/bookservices.service';
import { CartservicesService } from '../services/cartservices.service';
import { WishlistComponent } from '../wishlist/wishlist.component';
import { WishlistService } from '../services/wishlistservices.service';

interface Book {
  book_id: number;
  title: string;
  author_name: string;
  published_date: string;
  rating: number;
  stock: number;
  isbn: string;
  price: number;
  cover_image_url: string;
  description: string;
  favorited?: boolean;

}

interface Review {
  username: string;
  created_at: string;
  rating: number;
  comment: string;
}

@Component({
  selector: 'app-book',
  templateUrl: './book.component.html',
  styleUrls: ['./book.component.css']
})
export class BookComponent implements OnInit {
  book: Book | null = null;
  errorMessage: string = '';
  quantity: number = 1;
  userId: string = '';
  currentUser = { username: '' }; 
  reviews: Review[] = [];
  bookId: number | undefined;
  rating: number = 0;
  feedback: string = '';
  isCustomer: boolean = true;
  alertMessage: string | null = null;
  showErrors: any;


  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private bookService: BookservicesService,
    private cartService: CartservicesService,
    private wishlistService: WishlistService
  ) {}

  ngOnInit(): void {
    this.userId = localStorage.getItem('userId') || ''; 
    const title = this.route.snapshot.paramMap.get('title') || '';
    this.getBookDetails(title);
    this.fetchCurrentUser();
  }

  fetchCurrentUser(): void {
    const storedUser = localStorage.getItem('username'); 
    if (storedUser) {
      this.currentUser.username = storedUser;
    }
  }

  getBookDetails(title: string): void {
    this.bookService.bookDetailsByTitle(title).subscribe(
      response => {
        this.book = response;
        this.bookId = response.book_id;
        this.loadReviews();
      },
      error => {
        this.errorMessage = 'Error fetching book details.';
      }
    );
  }

  toggleFavorite(book: any): void {
    const wishlistId = localStorage.getItem('wishlist_id');
    this.alertMessage = null;
    
    if (!wishlistId) {
      console.error("Wishlist ID is missing. Please log in or create a wishlist first.");
      return;
    }
    
    if (book.favorited) {
      // If already favorited, remove from wishlist
      this.wishlistService.removeFromWishlist(book.book_id).subscribe({
        next: (response) => {
          book.favorited = false; // Update the status
          this.alertMessage = `Book removed from the Wishlist.`;
          console.log('Book removed from wishlist:', response);
        },
        error: (error) => {
          console.error('Error removing book from wishlist:', error);
        }
      });
    } else {
      // If not favorited, add to wishlist
      const item = {
        wishlist_id: wishlistId,
        bookId: book.book_id
      };
    
      this.wishlistService.addToWishlist(item).subscribe({
        next: (response) => {
          book.favorited = true; // Update the status
          this.alertMessage = `Book added to wishlist`;
          console.log('Book added to wishlist:', response);
        },
        error: (error) => {
          console.error('Error adding book to wishlist:', error);
        }
      });
    }
  }

  loadReviews(): void {
    if (this.bookId) {
      this.bookService.getReviews(this.bookId).subscribe(
        data => this.reviews = data.reviews,
        error => console.error('Failed to fetch reviews:', error)
      );
    }
  }

  getStars(rating: number): { type: 'filled' | 'empty'; filled: boolean }[] {
    return Array.from({ length: 5 }, (_, i) => ({
      type: i < rating ? 'filled' : 'empty',
      filled: i < rating
    }));
  }

  setRating(value: number): void {
    this.rating = value;
  }

  submitReview() {
    // Reset error messages
    this.errorMessage = '';
    this.alertMessage = '';
    
    // Check for missing fields
    this.showErrors = true; // This will trigger the error messages in the HTML
  
    if (!this.feedback) {
      console.error("Feedback is required.");
      this.errorMessage = 'Please provide your feedback.';
      return;
    }
  
    if (this.rating === 0) {
      console.error("Rating is required.");
      this.errorMessage = 'Please select a rating.';
      return;
    }
  
    if (!this.bookId) {
      console.error("Book ID is missing.");
      this.errorMessage = 'Error: Book ID is missing.';
      return;
    }
  
    // If all fields are filled, proceed to submit the review
    const review = {
      rating: this.rating,
      comment: this.feedback
    };
  
    this.bookService.submitReview(review, this.bookId).subscribe(
      response => {
        console.log('Review submitted successfully:', response);
        this.alertMessage = 'Review submitted successfully!';
        this.loadReviews(); // Refresh the reviews list
        this.feedback = ''; // Reset feedback
        this.rating = 0;    // Reset rating
        this.showErrors = false; // Reset error display
      },
      error => {
        console.error('Error submitting review:', error);
        this.errorMessage = 'Failed to submit review. Please try again later.';
      }
    );
  }
  

  increaseQuantity(): void {
    if (this.book && this.quantity < this.book.stock) {
      this.quantity++;
    }
  }

  decreaseQuantity(): void {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  BuyNow(): void {
    this.addToCart();
    this.router.navigate(['/cart']);
  }

  addToCart(): void {
    const cartId = localStorage.getItem('cart_id');  
    this.alertMessage = null;

    if (!cartId) {
      this.errorMessage = 'Cart not found. Please login again.';
      return;
    }

    if (this.book) { 
      const cartItem = {
        cart_id: cartId,
        bookId: this.book.book_id,
        quantity: this.quantity
      };

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
  }
}
