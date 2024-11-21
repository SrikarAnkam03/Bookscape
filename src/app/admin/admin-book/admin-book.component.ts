import { Component, OnInit } from '@angular/core';
import { ActivatedRoute} from '@angular/router';
import { Router } from '@angular/router';
import { BookservicesService } from '../services/bookservices.service';

interface Book {
  book_id: number;
  title: string;
  author_name: string;
  published_date: string;
  rating: number;
  stock: number;
  isbn: string;
  price: number;
  cover_image_url: string;
  description: string;
}

@Component({
  selector: 'app-admin-book',
  templateUrl: './admin-book.component.html',
  styleUrls: ['./admin-book.component.css']
})
export class AdminBookComponent implements OnInit {
  book: Book | null = null;
  bookId: number | undefined;
  title!: string;
  rating: number = 0;
  errorMessage: string = '';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private bookService: BookservicesService,
  ) {}

  ngOnInit(): void {
    const title = this.route.snapshot.paramMap.get('title') || '';
    this.getBookDetails(title);  
  }

  getBookDetails(title: string): void {
    this.bookService.bookDetailsByTitle(title).subscribe(
      response => {
        this.book = response;
        this.bookId = response.book_id;
      },
      error => {
        this.errorMessage = 'Error fetching book details.';
      }
    );
  }

  getStars(rating: number): { type: 'filled' | 'empty'; filled: boolean }[] {
    return Array.from({ length: 5 }, (_, i) => ({
      type: i < rating ? 'filled' : 'empty',
      filled: i < rating
    }));
  }

  logout(): void {
    localStorage.removeItem('authToken');
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
