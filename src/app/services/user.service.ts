import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private baseUrl = 'http://127.0.0.1:5000';
  private apiUrlSignup = `${this.baseUrl}/signup`;
  private apiUrlLogin = `${this.baseUrl}/login`;
  private apiUrlGetUser = `${this.baseUrl}/user`;
  private apiUrlSeller = `${this.baseUrl}/seller`;
  private apiUrlDelete = `${this.baseUrl}/delete`;
  private apiUrlUpdateUser = `${this.baseUrl}/update`;
  private apiUrlUsers = `${this.baseUrl}/users`;
  private apiUrlSellers = `${this.baseUrl}/sellers`;
  private apiUrlChangePassword = `${this.baseUrl}/change-password`;

  constructor(private http: HttpClient, private router: Router) { }

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Missing token'),
      localStorage.clear()
    }
    return new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  }
  
  signup(userData: any): Observable<any> {
    return this.http.post<any>(this.apiUrlSignup, userData).pipe(
      catchError((error) => {
        console.error('Signup error:', error);
        return throwError(error);
      })
    );
  }

  seller(userData: any): Observable<any> {
    return this.http.post<any>(this.apiUrlSeller, userData).pipe(
      catchError((error) => {
        console.error('Seller error:', error);
        return throwError(error);
      })
    );
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post<any>(this.apiUrlLogin, { email, password }).pipe(
      tap((response) => {
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('userId', response.user_id);
          localStorage.setItem('username', response.username)
          localStorage.setItem('role_name', response.role_name);
        }
      }),
      catchError((error) => {
        console.error('Login error:', error);
        return throwError(error);
      })
    );
  }

  getSellerDetails(username: string): Observable<any> {
    const url = `${this.apiUrlSeller}/${username}`;
    return this.http.get<any>(url, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        console.error('Error fetching seller details:', error);
        return throwError(error);
      })
    );
  }

  approveSeller(sellerData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrlSeller}/accept`, sellerData, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        console.error('Seller approval error:', error);
        return throwError(error);
      })
    );
  }

  rejectSeller(sellerData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrlSeller}/reject`, sellerData, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        console.error('Seller rejection error:', error);
        return throwError(error);
      })
    );
  }

  deleteSeller(sellerId: any): Observable<any> {
    return this.http.delete<any>(`${this.apiUrlDelete}/${sellerId}`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        console.error('Error deleting seller:', error);
        return throwError(error);
      })
    );
  }

  getUserDetails(): Observable<any> {
    return this.http.get(this.apiUrlGetUser, { headers: this.getAuthHeaders() }).pipe(
      catchError((error) => {
        console.error('Error fetching user details:', error);
        return throwError(error);
      })
    );
  }

  getUsers(): Observable<any> {
    return this.http.get(this.apiUrlUsers, { headers: this.getAuthHeaders() }).pipe(
      catchError((error) => {
        console.error('Error fetching users:', error);
        return throwError(error);
      })
    );
  }

  getSellers(): Observable<any> {
    return this.http.get(this.apiUrlSellers, { headers: this.getAuthHeaders() }).pipe(
      catchError((error) => {
        console.error('Error fetching sellers:', error);
        return throwError(error);
      })
    );
  }
  

  updateUserProfile(updatedProfile: any): Observable<any> {
    return this.http.put<any>(this.apiUrlUpdateUser, updatedProfile, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        console.error('Error updating profile:', error);
        return throwError(error);
      })
    );
  }

  changePassword(passwordData: any): Observable<any> {
    return this.http.put<any>(this.apiUrlChangePassword, passwordData, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        console.error('Error changing password:', error);
        return throwError(error);
      })
    );
  }

  get isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  get user_id(): string | null {
    return localStorage.getItem('userId');
  }

  get role_name(): string | null {
    return localStorage.getItem('role_name');
  }
}
