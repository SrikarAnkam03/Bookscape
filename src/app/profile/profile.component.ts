import { Component, OnInit } from '@angular/core';
import { UserService } from '../services/user.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  user: any;
  userId: string = '';
  email: string = '';
  userName: string = '';
  phoneNumber: string = '';
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
        this.phoneNumber = response.phone_number;
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
    this.showModal = false;
  }
  
  onSubmit() {
    const updatedProfile = {
      user_id: this.userId,  
      email: this.email,
      username: this.userName,
      phone: this.phoneNumber
    };

    console.log('Sending update request with:', updatedProfile); 
    this.userService.updateUserProfile(updatedProfile).subscribe(
      (response) => {
        console.log('Profile updated successfully', response);
        Swal.fire({
          title: response.message,
          icon: 'success',
          confirmButtonColor: '#3399c9',
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
      console.error('New password and confirmation do not match');
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
        this.closeChangePasswordModal();
      },
      (error) => {
        console.error('Error changing password:', error);
      }
    );
  }

  onPhoneNumberInput() {
    this.phoneNumber = this.phoneNumber.replace(/[^0-9]/g, '');
  }
}
