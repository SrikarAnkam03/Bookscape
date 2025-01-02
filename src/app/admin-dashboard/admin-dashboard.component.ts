import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UserService } from '../services/user.service';
import { BookservicesService } from '../services/bookservices.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  sellerUsername!: string;
  books: any[] = [];
  showBookHeaders: boolean = false;
  sellerDetails!: any; 

  currentPage: number = 1;
  itemsPerPage: number = 10;
  paginatedBooks: any[] = [];
  totalPages: number = 0;

  constructor(
    private route: ActivatedRoute,
    private bookService: BookservicesService,
    private userService: UserService,
    private router: Router
  ) {}


  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.sellerUsername = params.get('username')!;
      if (this.sellerUsername) {
        this.showBookHeaders = true;
        this.fetchSellersBooks();
        this.fetchSellerDetails();
      }
    });
  }

  fetchSellersBooks(): void {
    this.bookService.adminSellerbooks(this.sellerUsername).subscribe(
      (response: any) => {
        this.books = response.books;
        this.calculateTotalPages();
        this.updatePaginatedBooks();
    }, 
    (error) => {
      console.error('Error fetching seller books:', error);
    });
  }

  fetchSellerDetails(): void {
    this.userService.getSellerDetails(this.sellerUsername).subscribe(
      (data: any) => {
        this.sellerDetails = data;
        console.log('Seller details:', this.sellerDetails);
      },
      error => {
        console.error('Error fetching seller details:', error);
      }
    );
  }

  calculateTotalPages(): void {
    this.totalPages = Math.ceil(this.books.length / this.itemsPerPage);
  }

  updatePaginatedBooks(): void {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    this.paginatedBooks = this.books.slice(startIndex, endIndex);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.updatePaginatedBooks();
    }
  }

  prevPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.updatePaginatedBooks();
    }
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