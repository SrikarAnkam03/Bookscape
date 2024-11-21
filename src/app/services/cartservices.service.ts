import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CartservicesService {

  private baseUrl = 'http://127.0.0.1:5000';
  private apiUrlCart = `${this.baseUrl}/cart`;
  private apiUrlCartItems = `${this.baseUrl}/cartItems`;

  private cartCountSubject = new BehaviorSubject<number>(0); 
  cartCount$ = this.cartCountSubject.asObservable(); 

  constructor(private http: HttpClient) { }

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

  getCartCount(): number {
    return isNaN(this.cartCountSubject.value) ? 0 : this.cartCountSubject.value;
  }


  setCartCount(count: number): void {
    this.cartCountSubject.next(count);
  }

  createCart(userId: string): Observable<any> {
    const headers = this.getHeaders();
    const body = { userId };
    return this.http.post(this.apiUrlCart, body, { headers }).pipe(
      catchError((error) => {
        console.error('Error creating cart:', error);
        return throwError(error);
      })
    );
  }

  addCartItem(cartItem: any): Observable<any> {
    return this.http.post(this.apiUrlCartItems, cartItem, { headers: this.getHeaders() }).pipe(
      tap(() => {
        const currentCount = this.getCartCount();
        this.setCartCount(currentCount + 1); 
      }),
      catchError((error) => {
        console.error('Error adding cart item:', error);
        return throwError(error);
      })
    );
  }

  // Get all items in the cart for a given cart ID
  getCartItems(cartId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrlCartItems}?cart_id=${cartId}`, { headers: this.getHeaders() }).pipe(
      tap((items) => this.setCartCount(items.length)),
      catchError((error) => {
        console.error('Error fetching cart items:', error);
        return throwError(error);
      })
    );
  }

  // Update the quantity of an existing cart item
  updateCartItemQuantity(cartItemId: string, quantity: number): Observable<any> {
    return this.http.put(`${this.apiUrlCartItems}/${cartItemId}`, { quantity }, { headers: this.getHeaders() }).pipe(
      tap(() => this.updateCartCount()), // Update cart count after modifying item
      catchError((error) => {
        console.error('Error updating cart item quantity:', error);
        return throwError(error);
      })
    );
  }

  // Remove an item from the cart
  removeCartItem(cartItemId: string): Observable<any> {
    return this.http.delete(`${this.apiUrlCartItems}/${cartItemId}`, { headers: this.getHeaders() }).pipe(
      tap(() => this.updateCartCount()), // Update cart count after removing item
      catchError((error) => {
        console.error('Error removing cart item:', error);
        return throwError(error);
      })
    );
  }

  // Private method to update cart count from the server
  private updateCartCount() {
    const cartId = localStorage.getItem('cart_id'); // Ensure you have a cart ID stored in localStorage
    if (cartId) {
      this.getCartItems(cartId).subscribe({
        next: (items) => this.setCartCount(items.length),
        error: () => this.setCartCount(0)
      });
    }
  }

  // Clear the cart count when user logs out
  clearCartCount() {
    this.setCartCount(0);
  }
}
