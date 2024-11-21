import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class BookservicesService {
  private apiUrlBook = 'http://127.0.0.1:5000/book'; 
  private apiUrlSellerBooks = 'http://127.0.0.1:5000/sellerBooks';
  private apiUrlAdminSellerBooks = 'http://127.0.0.1:5000/adminSellerBooks';
  private apiUrlBooks = 'http://127.0.0.1:5000/books';
  private apiUrlReviews = 'http://127.0.0.1:5000/reviews';

  constructor(private http: HttpClient, private router: Router) {}

  // Retrieves authorization headers with JWT
  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      localStorage.clear();
      this.router.navigate(['/login']); 
      throw new Error('Missing token');
    }
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  // Fetch a single book
  book(): Observable<any> {
    return this.http.get(this.apiUrlBook, { headers: this.getAuthHeaders() }).pipe(
      tap((data) => console.log('Fetched books:', data)),
      catchError(this.handleError)
    );
  }

  // Fetch all books
  getBooks(): Observable<any> {
    return this.http.get(this.apiUrlBooks, { headers: this.getAuthHeaders() }).pipe(
      tap((data) => console.log('Fetched books:', data)),
      catchError(this.handleError)  
    );
  }

  // Fetch seller's books
  sellerbooks(): Observable<any> {
    return this.http.get(this.apiUrlSellerBooks, { headers: this.getAuthHeaders() }).pipe(
      tap((data) => console.log('Fetched seller books:', data)),
      catchError(this.handleError)
    );
  }

  // Fetch seller books for admin with seller username
  adminSellerbooks(sellerUsername: string): Observable<any> {
    const params = new HttpParams().set('username', sellerUsername);
    return this.http.get(this.apiUrlAdminSellerBooks, { 
      headers: this.getAuthHeaders(),
      params 
    }).pipe(
      tap((data) => console.log('Fetched admin seller books:', data)),
      catchError(this.handleError)
    );
  }

  // Get book details by title
  bookDetailsByTitle(title: string): Observable<any> {
    const params = new HttpParams().set('title', title);
    return this.http.get<any>(this.apiUrlBook, { headers: this.getAuthHeaders(), params }).pipe(
        catchError(this.handleError)
    );  
  }

  // Add a new book
  addBook(newBook: any): Observable<any> {
    let headers = this.getAuthHeaders();
  
    if (newBook instanceof FormData) {
      headers = headers.delete('Content-Type');
    }
    return this.http.post(this.apiUrlBook, newBook, { headers }).pipe(
      tap((data) => console.log('Added book:', data)),
      catchError(this.handleError)
    );
  }
  

  // Update book by title
  updateBook(title: any): Observable<any> {
    console.log('Updating book:', title);
    return this.http.put(this.apiUrlBook, title, { headers: this.getAuthHeaders() }).pipe(
        tap((data) => console.log('Updated book:', data)),
        catchError(this.handleError)
    );
  }

  // Delete a book by its ID
  deleteBook(bookId: string): Observable<any> {
    return this.http.delete(this.apiUrlBook, {
      body: { bookId },
      headers: this.getAuthHeaders()
    }).pipe(
      tap((data) => console.log('Deleted book:', data)),
      catchError(this.handleError)
    );
  }

  // Fetch reviews for a specific book
  getReviews(bookId: number): Observable<any> {
    const params = new HttpParams().set('book_id', bookId.toString());
    return this.http.get(this.apiUrlReviews, { headers: this.getAuthHeaders(), params }).pipe(
      tap((data) => console.log('Fetched reviews:', data)),
      catchError(this.handleError)
    );
  } 

  // ADD reviews for a specific book
  submitReview(review: { rating: number; comment: string; }, bookId: number): Observable<any> {
    const headers = this.getAuthHeaders().set('Content-Type', 'application/json');
    const body = { ...review, book_id: bookId };  
    return this.http.post(`${this.apiUrlReviews}/add`, body, { headers }).pipe(
      tap((data) => console.log('Review submitted successfully:', data)),
      catchError(this.handleError)
    );
  }
  

  private handleError(error: any): Observable<never> {
    console.error('An error occurred:', error);
    return throwError(error.message || 'Server error');
  }
}
