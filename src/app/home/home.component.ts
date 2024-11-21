import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CartservicesService } from '../services/cartservices.service';
import { WishlistService } from '../services/wishlistservices.service';
import { BookservicesService } from '../services/bookservices.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  books: any[] = [];
  filteredBooks: any[] = [];
  wishlist: any[] = [];
  searchTerm: string = '';
  errorMessage: string = '';
  quantity: number = 1;
  userId: string = localStorage.getItem("userId") || ''; 
  alertMessage: string | null = null;
  noResultsMessage: string = ''; 

  constructor(
    private router: Router,
    private cartService: CartservicesService,
    private wishlistService: WishlistService,
    private bookService: BookservicesService
  ) {}

  ngOnInit(): void {
    this.fetchBooks(); 
  }

  fetchBooks(): void {
    this.bookService.getBooks().subscribe({
      next: (data) => {
        this.books = data; 
        this.filteredBooks = [...this.books];
        console.log('Books fetched successfully:', this.books);
      },
      error: (err) => {
        this.errorMessage = err;
        console.error('Error fetching books:', err);
      }
    });
  }

  onSearch(): void {
    if (this.searchTerm.trim() !== '') {
      const results = this.books.filter(book =>
        book.title.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        book.author_name.toLowerCase().includes(this.searchTerm.toLowerCase())
      );

      if (results.length > 0) {
        this.filteredBooks = results;
        this.noResultsMessage = ''; 
        console.log('Search results:', results);
      } else {
        this.filteredBooks = [];
        this.noResultsMessage = 'No books found matching your search criteria.'; 
        console.log(this.noResultsMessage);
      }
    } else {
      this.filteredBooks = [...this.books]; 
      this.noResultsMessage = ''; 
    }
  }

  clearSearch(): void {
    this.searchTerm = '';
    this.filteredBooks = [...this.books]; 
    this.noResultsMessage = '';
  }

  viewBookDetails(title: string): void {
    this.router.navigate(['/book', title]);
  }

  addToCart(book: any): void {
    const cartItem = {
      cart_id: localStorage.getItem('cart_id'),
      bookId: book.book_id,
      quantity: this.quantity
    };

    this.cartService.addCartItem(cartItem).subscribe(
      (response) => {
        this.alertMessage = `${book.title} has been added to the cart.`;
        console.log('Item added to cart:', response);
      },
      (error) => {
        console.error('Error adding item to cart:', error);
      }
    );
  }

  isBookVisible(book: any): boolean {
    if (this.searchTerm.trim() === '') {
      return true; 
    }
    return book.title.toLowerCase().includes(this.searchTerm.toLowerCase()) || 
           book.author_name.toLowerCase().includes(this.searchTerm.toLowerCase());
  }
  

toggleFavorite(book: any): void {
  const wishlistId = localStorage.getItem('wishlist_id');
  this.alertMessage = null;
  if (!wishlistId) {
    console.error("Wishlist ID is missing. Please log in or create a wishlist first.");
    return;
  }

  if (book.favorited) {
    this.wishlistService.removeFromWishlist(book.book_id).subscribe({
      next: (response) => {
        book.favorited = false;
        this.alertMessage = `Book removed from the Wishlist.`;
        console.log('Book removed from wishlist:', response);
      },
      error: (error) => {
        console.error('Error removing book from wishlist:', error);
      }
    });
  } else {
    const item = {
      wishlist_id: wishlistId,
      bookId: book.book_id
    };

    this.wishlistService.addToWishlist(item).subscribe({
      next: (response) => {
        book.favorited = true;
        this.alertMessage = `Book added to wishlist`;
        console.log('Book added to wishlist:', response);
      },
      error: (error) => {
        console.error('Error adding book to wishlist:', error);
      }
    });
  }
}

}
