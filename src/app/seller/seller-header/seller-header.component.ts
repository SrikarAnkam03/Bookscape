import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-seller-header',
  templateUrl: './seller-header.component.html',
  styleUrls: ['./seller-header.component.css']
})
export class SellerHeaderComponent implements OnInit {
  isSidebarOpen = false; 

  constructor() { }

  ngOnInit(): void { }

  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  logout(): void {  
    localStorage.clear()
  }
}
