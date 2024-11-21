import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  private apiUrlOrders = 'http://127.0.0.1:5000/orders';
  userId: string | null = '';

  constructor(private http: HttpClient) {}

  getAllOrders(): Observable<any> { 
    const headers = this.getAuthHeaders(); 
    
    return this.http.get<any>(`${this.apiUrlOrders}/admin`, { headers })  
      .pipe(catchError(this.handleError));
  }

  getOrderById(orderId: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.get<any>(`${this.apiUrlOrders}/admin/${orderId}`, { headers })
      .pipe(catchError(this.handleError));
  }  

  placeOrder(address_id: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.post<any>(this.apiUrlOrders, { address_id }, { headers })
      .pipe(catchError(this.handleError));
  }

  getUserOrders(): Observable<any> {
    const headers = this.getAuthHeaders();
    this.userId = localStorage.getItem('userId')
    return this.http.get<any>(`${this.apiUrlOrders}?user_id=${this.userId}`, { headers })
      .pipe(catchError(this.handleError));
  }

  getSellerOrders(): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.get<any>(`${this.apiUrlOrders}/seller`, { headers })
      .pipe(catchError(this.handleError));
  }


  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Missing token');
    }
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(error);
  }
}
