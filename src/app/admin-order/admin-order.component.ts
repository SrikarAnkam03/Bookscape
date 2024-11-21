import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrderService } from '../services/order.service';

@Component({
  selector: 'app-admin-order',
  templateUrl: './admin-order.component.html',
  styleUrls: ['./admin-order.component.css']
})
export class AdminOrderComponent implements OnInit {
  orderId: string = '';
  orderDetails: any;
  items: any[] = [];
  errorMessage: string = '';
  loading: boolean = false;

  constructor(
    private orderService: OrderService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.orderId = params['order_id'];
      this.fetchOrderItems();
    });
  }

  fetchOrderItems(): void {
    this.loading = true; // Show loading indicator
    this.orderService.getOrderById(this.orderId).subscribe(
      (response) => {
        this.orderDetails = response.order;
        this.items = response.order.items;
        this.loading = false;
      },
      (error) => {
        this.loading = false;
        console.error('Failed to fetch order:', error);
        if (error.status === 404) {
          this.errorMessage = 'Order not found.';
        } else if (error.status === 401) {
          this.errorMessage = 'You are not authorized to view this order.';
          this.router.navigate(['/login']); 
        } else if (error.status === 500) {
          this.errorMessage = 'Server error. Please try again later.';
        } else {
          this.errorMessage = 'An unexpected error occurred. Please try again.';
        }
      }
    );
  }
}
