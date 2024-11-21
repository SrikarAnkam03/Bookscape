import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EmailVerificationOtpService {
  private baseUrl = 'http://127.0.0.1:5000/emailOtp'; 

  constructor(private http: HttpClient) {}

  sendOtp(email: string): Observable<any> {
    console.log(email)
    return this.http.post(`${this.baseUrl}/send-emailVerifyOtp`, { email });
  }

  verifyOtp(email: string, otp: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/verify-emailVerifyOtp`, { email, otp });
  }
}
