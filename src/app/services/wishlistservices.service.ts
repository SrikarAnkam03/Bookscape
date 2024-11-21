import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class WishlistService {

  private apiUrlwishlist = 'http://127.0.0.1:5000/wishlist';
  private apiUrlwishlistItems = 'http://127.0.0.1:5000/wishlistItems'; 

  constructor(private http: HttpClient) {}

  private createHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token'); 
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  createWishlist(userId: string): Observable<any> {
    const data = { userId };
    const headers = this.createHeaders();
    return this.http.post(this.apiUrlwishlist, data, { headers });
  }

  getWishlistItems(wishlistId: string): Observable<any> {
    const url = `${this.apiUrlwishlistItems}?wishlist_id=${wishlistId}`;
    const headers = this.createHeaders();
    return this.http.get<any>(url, { headers });
  }
  
  addToWishlist(item: { wishlist_id: string, bookId: string }): Observable<any> {
    const headers = this.createHeaders();
    return this.http.post(this.apiUrlwishlistItems, item, { headers });
  }
  
  removeFromWishlist(bookId: string): Observable<any> {
    const url = `${this.apiUrlwishlistItems}`; 
    const headers = this.createHeaders();
    return this.http.delete(url, { body: { bookId }, headers });
  }

}
