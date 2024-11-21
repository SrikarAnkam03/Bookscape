import { Component, OnInit } from '@angular/core';
import { OrderService } from '../services/order.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-orders',
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.css']
})
export class OrdersComponent implements OnInit {
  orders: any[] = [];

  constructor(
    private orderService: OrderService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.fetchOrders(); 
  }

  fetchOrders(): void {
    this.orderService.getUserOrders().subscribe(response => {
        this.orders = response.orders;
      },
      (error) => {
        console.error('Error fetching orders:', error);
      }
    );
  }

  viewBookDetails(bookTitle: string): void {
    this.router.navigate(['/book', bookTitle]);
  }
}
