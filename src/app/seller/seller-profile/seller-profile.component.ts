import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user.service';
import Swal from 'sweetalert2';

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
        Swal.fire('Error', 'Failed to fetch user details. Please try again.', 'error');
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
      (response) => {
        console.log('Profile updated successfully', response);
        Swal.fire({
          title: response.message,
          icon: 'success',
          confirmButtonColor: '#2C3E50',
          confirmButtonText: 'Okay',
          showCloseButton: true
        });        
        this.closeEditModal();
      },
      (error) => {
        console.error('Error updating profile', error);
        Swal.fire('Error', error.error.message || 'Failed to update profile. Please try again.', 'error');
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
      Swal.fire('Error', 'New password and confirmation do not match!', 'error');
      return;
    }
  
    const passwordChangeRequest = {
      current_password: this.currentPassword,
      new_password: this.newPassword,
      email: this.email
    };
    console.log('Sending password change request:', passwordChangeRequest);
  
    this.userService.changePassword(passwordChangeRequest).subscribe(
      (response) => {
        console.log('Password changed successfully:', response);
        Swal.fire({
          title: response.message,
          icon: 'success',
          confirmButtonColor: '#2C3E50',
          confirmButtonText: 'Okay',
          showCloseButton: true
        });
        this.closeChangePasswordModal();
      },
      (error) => {
        console.error('Error changing password:', error);
        Swal.fire('Error', error.error.message || 'Failed to change password. Please try again.', 'error');
      }
    );
  }

  onPhoneNumberInput() {
    this.phone_number = this.phone_number.replace(/[^0-9]/g, '');
  }
}
