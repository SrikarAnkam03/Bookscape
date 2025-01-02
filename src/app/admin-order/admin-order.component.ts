import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrderService } from '../services/order.service';
import Swal from 'sweetalert2';

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

  logout(): void {
    Swal.fire({
      title: 'Are you sure you want to log out?',
      showCancelButton: true,
      confirmButtonColor: '#004d88',
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
