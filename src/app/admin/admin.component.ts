import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserService } from '../services/user.service';
import { Router } from '@angular/router';
import { BookservicesService } from '../services/bookservices.service';
import { OrderService } from '../services/order.service';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  users: any[] = [];
  books: any[] = [];
  orders: any[] = [];
  sellers: any[] = [];
  selectedBox: string = '';
  seller: any;
  isDeleteModal = false;
  isStatusModal = false;

  showUserHeaders: boolean = false;
  showBookHeaders: boolean = false;
  showOrderHeaders: boolean = false;
  showSellerHeaders: boolean = false;

  isSidebarOpen: boolean = true;

  // Pagination Variables
  currentPage: number = 1;
  itemsPerPage: number = 10; 
  totalItems: number = 0;

  sortColumn: string = '';
  sortDirection: 'asc' | 'desc' = 'asc'; 
  
  constructor(
    private bookService: BookservicesService,
    private orderService: OrderService,
    private userService: UserService,
    private http: HttpClient,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.checkAuthAndFetchData();
      this.fetchData('orders');
  }

  checkAuthAndFetchData(): void {
    const authToken = localStorage.getItem('access_token');
    if (authToken) {
      this.fetchData('sellers');
      this.fetchData('users');
      this.fetchData('books');
    } else {
      this.router.navigate(['/login']);
    }
  }

  toggleSidebar() {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  navigateToDashboard(sellerUsername: string): void {
    this.router.navigate(['admin/', sellerUsername]);
  }

  navigateToBook(title: string): void {
    this.router.navigate(['adminBook', title]);
  }

  navigateToOrder(order_id: string): void {
    this.router.navigate(['order', order_id]);
  }

  fetchData(type: string): void {
    this.selectedBox = type;
    this.currentPage = 1;
    switch (type) {
      case 'users':
        this.userService.getUsers().subscribe(data => {
          this.users = data.data;
          this.totalItems = this.users.length;
          this.sortData(this.users);
          this.showUserHeaders = true;
          this.showBookHeaders = false;
          this.showOrderHeaders = false;
          this.showSellerHeaders = false;
        });
        break;
      case 'books':
        this.bookService.getBooks().subscribe(data => {
          this.books = data;
          this.totalItems = this.books.length;
          this.sortData(this.books);
          this.showUserHeaders = false;
          this.showBookHeaders = true;
          this.showOrderHeaders = false;
          this.showSellerHeaders = false;
        });
        break;
      case 'orders':
        this.orderService.getAllOrders().subscribe(data => {
          this.orders = data.orders;
          this.totalItems = this.orders.length;
          this.sortData(this.orders);
          this.showUserHeaders = false;
          this.showBookHeaders = false;
          this.showOrderHeaders = true;
          this.showSellerHeaders = false;
        });
        break;
      case 'sellers':
        this.userService.getSellers().subscribe(data => {
          this.sellers = data.data;
          this.sellers.forEach(seller => {
            seller.hoverText = seller.approve ? '<i class="uil uil-check"></i>' : '<i class="uil uil-times"></i>';
            seller.hoverColor = seller.approve ? '#5dee89' : '#dddddd';
          });
          this.totalItems = this.sellers.length;
          this.sortData(this.sellers);
          this.showUserHeaders = false;
          this.showBookHeaders = false;
          this.showOrderHeaders = false;
          this.showSellerHeaders = true;
        });
        break;
      default:
        break;
    }
  }

  // Sorting Helper Function
  sortData(data: any[]): void {
    if (!this.sortColumn) return; 

    data.sort((a, b) => {
      if (a[this.sortColumn] < b[this.sortColumn]) {
        return this.sortDirection === 'asc' ? -1 : 1;
      } else if (a[this.sortColumn] > b[this.sortColumn]) {
        return this.sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }

  // Method to toggle sort direction and column
  sortTable(column: string): void {
    if (this.sortColumn === column) {
      // If the same column is clicked, toggle direction
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      // Otherwise, set new column and default direction to ascending
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.fetchData(this.selectedBox); // Re-fetch and sort data
  }

  // Pagination Helpers
  getPaginatedData(data: any[]): any[] {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    return data.slice(startIndex, startIndex + this.itemsPerPage);
  }

  changePage(page: number): void {
    this.currentPage = page;
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.itemsPerPage);
  }

  generatePageNumbers(): number[] {
    return Array(this.totalPages).fill(0).map((_, index) => index + 1);
  }

  openRemoveModal(seller: any): void {
    this.seller = seller;
    this.isDeleteModal = true;
  }

  closeModal(): void {
    this.isDeleteModal = false;
    this.isStatusModal = false;
    this.seller = null;
  }

  deleteSeller(): void {
    const sellerId = this.seller.user_id;
    if (sellerId) {
      this.userService.deleteSeller(sellerId).subscribe(
        () => {
          this.sellers = this.sellers.filter(seller => seller.user_id !== sellerId);
          this.closeModal();
          this.fetchData('sellers');
        },
        (error) => {
          console.error('Error deleting seller:', error);
          this.closeModal();
        }
      );
    }
  }

  openStatusModal(seller: any): void {
    this.seller = seller;
    this.isStatusModal = true;
  }

  toggleApproval(): void {
    if (this.seller) {
      if (this.seller.approve) {
        this.rejectSeller(this.seller);
      } else {
        this.approveSeller(this.seller);
      }
    }
  }

  approveSeller(seller: any): void {
    const sellerData = { user_id: seller.user_id };
    this.userService.approveSeller(sellerData).subscribe(
      (response: any) => {
        seller.approve = true;
        console.log(response.message);
        this.fetchData('sellers');
        this.closeModal();
      },
      (error: any) => {
        console.error('Approval error:', error);
      }
    );
  }

  rejectSeller(seller: any): void {
    const sellerData = { user_id: seller.user_id };
    this.userService.rejectSeller(sellerData).subscribe(
      (response: any) => {
        seller.approve = false;
        console.log(response.message);
        this.fetchData('sellers');
        this.closeModal();
      },
      (error: any) => {
        console.error('Rejection error:', error);
      }
    );
  }

  onMouseOver(seller: any): void {
    seller.hoverText = seller.approve 
      ? '<i class="uil uil-times"></i>'
      : '<i class="uil uil-check"></i>'; 
    seller.hoverColor = seller.approve ? '#bb2828' : '#20c000'; 
  }

  onMouseLeave(seller: any): void {
    seller.hoverText = seller.approve 
      ? '<i class="uil uil-check"></i>'
      : '<i class="uil uil-times"></i>';
    seller.hoverColor = seller.approve ? '#5dee89' : '#dddddd';
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
