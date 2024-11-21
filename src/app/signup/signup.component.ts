import { Component } from '@angular/core';
import { EmailVerificationOtpService } from '../services/email-verfication-otp.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { UserService } from '../services/user.service'; 
import { Router } from '@angular/router';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {
  registrationForm: FormGroup;
  otpForm: FormGroup;
  successMessage: string = '';
  errorMessage: string = '';
  isOtpSent = false;
  otpErrorMessage: string | null = null;

  countdown: number = 300;
  displayTime: string = '05:00';

  constructor(
    private otpService: EmailVerificationOtpService,
    private userService: UserService, 
    private fb: FormBuilder,
    private router: Router,
  ) {
    this.registrationForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(20)]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.required, Validators.pattern(/^\d{10}$/)]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    }, { validators: this.passwordMatchValidator });

    this.otpForm = this.fb.group({
      otp: ['', [Validators.required, Validators.pattern(/^\d{6}$/)]]
    });
  }

  validateNumberInput(event: KeyboardEvent): void {
    const key = event.key;
    if (!/[0-9.]/.test(key) && key !== 'Backspace' && key !== 'Tab' && key !== 'Enter') {
      event.preventDefault();
    }
  }

  passwordMatchValidator(formGroup: FormGroup) {
    const password = formGroup.get('password')?.value;
    const confirmPassword = formGroup.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  onSubmit() {
    this.successMessage = '';
    this.errorMessage = '';

    this.registrationForm.markAllAsTouched();

    if (this.registrationForm.hasError('passwordMismatch')) {
      this.errorMessage = 'Passwords do not match.';
      return;
    }

    if (this.registrationForm.valid) {
      const formData = this.registrationForm.value;

      const userData = {
        username: formData.username,
        email: formData.email,
        phone_number: formData.phone,
        users_pswd: formData.password,
        confirm_password: formData.confirmPassword
      };

      this.otpService.sendOtp(userData.email).subscribe(
        response => {
          this.successMessage = 'OTP sent to your email';
          console.log('OTP sent successfully:', response);
          this.isOtpSent = true;
          this.errorMessage = '';
          this.startTimer();
        },
        error => {
          console.error('Error sending OTP:', error);
          if (error.status===400 || 404){
              this.errorMessage = error.error.message
          }
        }
      );
    } else {
      this.errorMessage = 'Please fill in all required fields correctly.';
    }
  }

  startTimer(): void {
    this.countdown = 300;
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
      this.otpErrorMessage = 'Please enter a valid 6-digit OTP.';
      return;
    }
  
    const email = this.registrationForm.value.email;
    const otp = this.otpForm.value.otp;
  
    this.otpService.verifyOtp(email, otp).subscribe(
      (response) => {
        console.log('OTP verified successfully:', response);
        this.successMessage = 'OTP verified successfully! Registering your account...';
        this.isOtpSent = false;
  
        // Now call the signup method to create the user in the database
        const formData = this.registrationForm.value;
        const userData = {
          username: formData.username,
          email: formData.email,
          phone_number: formData.phone,
          users_pswd: formData.password,
          confirm_password: formData.confirmPassword
        };
  
        this.userService.signup(userData).subscribe(
          (signupResponse) => {
            this.successMessage = ('User registered successfully!');
            setTimeout(() => {
              this.router.navigate(['/login']);
            }, 2000);
          },
          (signupError) => {
            console.error('Error during signup:', signupError);
            this.errorMessage = signupError.error.message || 'Failed to create user. Please try again.';
          }
        );
      },
      (error) => {
        console.error('Error verifying OTP:', error);
        this.otpErrorMessage = error.error.message || 'Invalid OTP. Please try again.';
      }
    );
  }
  

  closeModal(){
    this.isOtpSent =false;
  }
}
