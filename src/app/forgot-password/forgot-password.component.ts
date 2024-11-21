import { Component, OnInit } from '@angular/core';
import { OtpService } from '../services/otp.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent implements OnInit {
  emailForm!: FormGroup;
  passwordForm!: FormGroup;
  otpForm!: FormGroup;
  errorMessage: string | null = null;
  showModal = false;
  isOtpSent = false;
  isPasswordReset = false;
  isLoading=false
  forgetErrorMessage:string|null=null
 
  countdown: number = 300; 
  displayTime: string = '05:00';
 
 
  constructor(
    private fb: FormBuilder,
    private router: Router,
    private otpService: OtpService
  ) {}
 
  ngOnInit() {
    this.emailForm=this.fb.group({
      email:['',[Validators.required,Validators.email]]
    });
    this.otpForm=this.fb.group({
      otp:['',[Validators.required,Validators.minLength(1)  ]]
    })
    this.passwordForm=this.fb.group({
      newPassword: ['', [Validators.required,
                         Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(8)]]
    })
  }  
 
  closeForgotPasswordModal() {
    this.showModal = false;
    this.isOtpSent = false;
    this.isPasswordReset = false;
    this.emailForm.reset();
    this.otpForm.reset();
    this.passwordForm.reset();
    this.errorMessage=null
  }
 
 
  onEmailSubmit() {
    this.otpService.sendOtp(this.emailForm.value).subscribe(
      data => {
        this.isOtpSent = true;
        this.errorMessage = '';
        this.startTimer()
        this.showModal = true;
      },
      error => {
      if (error.status === 404) {
          this.errorMessage = error.error.message;
      }
      else if (error.status === 400) {
        this.errorMessage=error.error.message
      }
      else {
        this.errorMessage = 'An unexpected error occurred. Please try again.';
      }
      }
    );
  }
 
  startTimer(): void {
    const timer = setInterval(() => {
      if (this.countdown > 0) {
        this.countdown--;
        const minutes = Math.floor(this.countdown / 60).toString().padStart(2, '0');
        const seconds = (this.countdown % 60).toString().padStart(2, '0');
        this.displayTime = `${minutes}:${seconds}`;
      } else {
        clearInterval(timer); 
      }
    }, 1000);
  }
 
  onOtpSubmit() {
    if (this.otpForm.invalid) {
      this.otpForm.markAllAsTouched();
      this.errorMessage='Please enter 6 digit otp'
      return;
    }
    const payload = { ...this.emailForm.value, ...this.otpForm.value };
    this.otpService.verifyOtp(payload).subscribe(
      data => {     
        this.isOtpSent = false;
        this.isPasswordReset = true;
        this.errorMessage = '';
      },
      error => {
        if (error.status === 400) {
          this.errorMessage=error.error.message
        }
        else {
          this.errorMessage = 'An unexpected error occurred. Please try again.';
        }
      }
    );
  }
 
  onPasswordSubmit() {
    if(this.passwordForm.value.newPassword!=this.passwordForm.value.confirmPassword){
      this.errorMessage='Password mis match'
      return 
    }
    const payload = {...this.emailForm.value, new_password: this.passwordForm.value.newPassword };
    this.otpService.resetPassword(payload).subscribe(
      response => {
        this.startTimer();
        alert(response.message);
        this.closeForgotPasswordModal();
        this.router.navigate(['/login']);
      },
      error => {
        if (error.status === 400) {
          this.errorMessage=error.error.message
        } else {
          this.errorMessage = 'Failed to reset password. Please try again.';
        }
      }
    );
  }
}

