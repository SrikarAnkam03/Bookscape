import { Component, OnInit } from '@angular/core';
import { OrderService } from 'src/app/services/order.service';

@Component({
  selector: 'app-seller-orders',
  templateUrl: './seller-orders.component.html',
  styleUrls: ['./seller-orders.component.css']
})
export class SellerOrdersComponent implements OnInit {
  orders: any[] = [];
  
  currentPage: number = 1;
  itemsPerPage: number = 5;
  paginatedOrders: any[] = [];
  totalPages: number = 0;

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.fetchSellerOrders();
  }

  fetchSellerOrders(): void {
    this.orderService.getSellerOrders().subscribe(
      (response: any) => {
        this.orders = response.orders;
        this.calculateTotalPages();
        this.updatePaginatedOrders();
        console.log(this.orders);
      },
      (error) => {
        console.error('Error fetching orders:', error);
      }
    );
  }

  // Calculate total pages based on orders length
  calculateTotalPages(): void {
    this.totalPages = Math.ceil(this.orders.length / this.itemsPerPage);
  }

  // Update the orders to display on the current page
  updatePaginatedOrders(): void {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    this.paginatedOrders = this.orders.slice(startIndex, endIndex);
  }

  // Navigate to the next page
  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.updatePaginatedOrders();
    }
  }

  // Navigate to the previous page
  prevPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.updatePaginatedOrders();
    }
  }
}
