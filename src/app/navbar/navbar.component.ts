import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { CartservicesService } from '../services/cartservices.service';
import { Subscription } from 'rxjs';

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
    this.cartService.clearCartCount(); 
    localStorage.clear();
    this.router.navigate(['/login']);
  }

  ngOnDestroy(): void {
    if (this.cartSubscription) {
      this.cartSubscription.unsubscribe();
    }
  }
}
