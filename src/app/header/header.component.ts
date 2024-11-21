import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  isSignupPage: boolean = false;
  isSellerPage: boolean = false;

  constructor(private router: Router) {}

  ngOnInit(): void {
    // Check the route on initialization
    this.checkCurrentRoute();

    // Subscribe to router events to detect route changes
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        this.checkCurrentRoute();
      }
    });
  }

  checkCurrentRoute(): void {
    const currentUrl = this.router.url;

    // Determine which page is currently active based on the URL
    this.isSignupPage = currentUrl === '/signup';
    this.isSellerPage = currentUrl === '/seller';
  }
}
