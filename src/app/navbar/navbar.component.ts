import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { CartservicesService } from '../services/cartservices.service';
import { Subscription } from 'rxjs';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit, OnDestroy {
  dropdownOpen: boolean = false;
  isSidebarOpen = false;
  isDropdownOpen = false;
  cartCount: number = 0;
  private cartSubscription!: Subscription;
  authService: any;

  constructor(private router: Router, private cartService: CartservicesService) { }

  ngOnInit(): void {
    this.cartSubscription = this.cartService.cartCount$.subscribe(count => {
      this.cartCount = count;
    });
  }

  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
  }
  
  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  logout(): void {
    Swal.fire({
      title: 'Are you sure you want to log out?',
      showCancelButton: true,
      confirmButtonColor: '#5cabff',
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
        // Perform logout operation
        this.cartService.clearCartCount(); 
        localStorage.clear();
        this.router.navigate(['/login']);
      }
    });
  }
  
  
  ngOnDestroy(): void {
    if (this.cartSubscription) {
      this.cartSubscription.unsubscribe();
    }
  }
}
