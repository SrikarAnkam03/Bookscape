import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OtpService {
  private apiUrlOtp = 'http://127.0.0.1:5000/otp';

  constructor(private http: HttpClient, private router: Router) { }

  sendOtp(email: any): Observable<any> {
    return this.http.post(`${this.apiUrlOtp}/send-otp`, email);
  }
 
  verifyOtp(data: any): Observable<any> {
    return this.http.post(`${this.apiUrlOtp}/verify-otp`, data);
  }
 
  resetPassword(data: any): Observable<any> {
    return this.http.post(`${this.apiUrlOtp}/reset-password`, data);
  }
}
