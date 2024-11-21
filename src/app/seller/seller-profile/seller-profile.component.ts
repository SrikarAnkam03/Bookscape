import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user.service';


@Component({
  selector: 'app-seller-profile',
  templateUrl: './seller-profile.component.html',
  styleUrls: ['./seller-profile.component.css']
})
export class SellerProfileComponent implements OnInit {
  user: any;
  userId: string = '';
  email: string = '';
  userName: string = '';
  phone_number: string = '';
  currentPassword: string = '';
  newPassword: string = '';
  confirmPassword: string = '';

  showModal: boolean = false;
  changePasswordModal: boolean = false;

 
  constructor(private userService: UserService) {}  

  ngOnInit(): void {
    this.getEmailFromLocalStorage();
    this.fetchUser();
  }

  getEmailFromLocalStorage(): void {
    this.email = localStorage.getItem('email') || '';
  }

  fetchUser(): void {
    console.log("Fetching user data for:", this.email);
  
    this.userService.getUserDetails().subscribe(
      (response: any) => {
        console.log("User data received:", response);
        this.email = response.email;
        this.userName = response.username;
        this.phone_number = response.phone_number;
      },
      (error) => {
        console.error('Error fetching user details:', error);
      }
    );
  }

  openEditModal() {
    this.showModal = true;
  }

  closeEditModal() {
    this.fetchUser();
    this.showModal = false;
  }
  
  onSubmit() {
    const updatedProfile = {
      user_id: this.userId,  
      email: this.email,
      username: this.userName,
      phone_number: this.phone_number
    };
    
    this.userService.updateUserProfile(updatedProfile).subscribe(
      response => {
        console.log('Profile updated successfully', response);
        this.closeEditModal();
      },
      error => {
        console.error('Error updating profile', error);
      }
    );
  }

  openChangePasswordModal() {
    this.changePasswordModal = true;
  }
  
  closeChangePasswordModal() {
    this.changePasswordModal = false;
  }

  onChangePasswordSubmit() {
    if (this.newPassword !== this.confirmPassword) {
      console.error('New password and confirmation do not match');
      return;
    }
  
    const passwordChangeRequest = {
      current_password: this.currentPassword,
      new_password: this.newPassword,
      email: this.email
    };
    console.log("🚀 ~ SellerProfileComponent ~ onChangePasswordSubmit ~ passwordChangeRequest.current_password:", passwordChangeRequest.current_password)
  
    console.log('Sending password change request:', passwordChangeRequest);
  
    this.userService.changePassword(passwordChangeRequest).subscribe(
      (response) => {
        console.log('Password changed successfully:', response);
        this.closeChangePasswordModal();
      },
      (error) => {
        console.error('Error changing password:', error);
      }
    );
  }

  onPhoneNumberInput() {
    this.phone_number = this.phone_number.replace(/[^0-9]/g, '');
  }
}
