import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-seller-header',
  templateUrl: './seller-header.component.html',
  styleUrls: ['./seller-header.component.css']
})
export class SellerHeaderComponent implements OnInit {
  isSidebarOpen = false; 

  constructor(private router: Router) { }

  ngOnInit(): void { }

  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  logout(): void {
    Swal.fire({
      title: 'Are you sure you want to log out?',
      showCancelButton: true,
      confirmButtonColor: '#2C3E50',
      cancelButtonColor: '#888',
      confirmButtonText: 'Yes',
      cancelButtonText: 'No',
      customClass: {
        popup: 'custom-swal-wide'
      },
      didOpen: () => {
        const popup = document.querySelector('.swal2-popup') as HTMLElement;
        const ButtonYes = document.querySelector('.swal2-confirm') as HTMLElement;
        const ButtonNo = document.querySelector('.swal2-cancel') as HTMLElement;
        if (ButtonYes) {
          ButtonYes.style.width = '100px';
        }
        if (ButtonNo) {
          ButtonNo.style.width = '100px';
        }
        if (popup) {
          popup.style.width = '380px';
          popup.style.height = '150px';
        }
      }
    }).then((result) => {
      if (result.isConfirmed) {
        localStorage.clear();
        this.router.navigate(['/login']);
      }
    });
  }
}
