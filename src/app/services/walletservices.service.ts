import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class WalletService {
  private apiUrlWallet = 'http://127.0.0.1:5000/wallet';


  constructor(private http: HttpClient) {}

  private createHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token'); 
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }
  
  createWallet(userId: string): Observable<any> {
    const data = { userId };
    const headers = this.createHeaders();
    return this.http.post(this.apiUrlWallet, data, { headers });
  }

  getBalance(): Observable<any> {
    const token = localStorage.getItem('access_token');  
    return this.http.get<any>(`${this.apiUrlWallet}/balance`, {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    })
    .pipe(
      catchError(this.handleError)
    );
  }

  deposit(amount: number): Observable<any> {
    const userId = localStorage.getItem('userId');

    if (!userId) {
      return throwError('User ID is required');
    }
    
    const numericAmount = parseFloat(amount.toString());
  
    return this.http.post<any>(`${this.apiUrlWallet}/deposit`, { userId, amount: numericAmount }) 
      .pipe(
        catchError(this.handleError)
      );
  }

  withdraw(amount: number): Observable<any> {
    const userId = localStorage.getItem('userId');
    return this.http.post<any>(`${this.apiUrlWallet}/withdraw`, { userId ,amount })
      .pipe(
        catchError(this.handleError)
      );
  }

  getTransactions(): Observable<any> {
    const token = localStorage.getItem('access_token');
    return this.http.get<any>(`${this.apiUrlWallet}/transactions`, {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`
      })
    }).pipe(
      catchError(this.handleError)
    );
  }
  

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(error);
  }
}
