import { Component, OnInit } from '@angular/core';
import { BookservicesService } from '../../services/bookservices.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

    isSidebarClosed = false;
    alertMessage: string | null = null;
    userName: string | null = localStorage.getItem('username');


  deletebook = { book_id: '', title: '' };  
  updatebook: any = {
    bookId: '',
    currentTitle: '',
    title: '',
    author_name: '',
    genre_name: '',
    price: null,
    stock: null,
    published_date: '',
    description: '',
    cover_image_url: '',
    isbn: '',
    rating: null
  };
  newBook: any = {
    title: '',
    author_name: '',
    genre_name: '',
    price: null,
    stock: null,
    published_date: '',
    description: '',
    cover_image_url: '',
    isbn: '',
    rating: null,
    user_id: localStorage.getItem('userId')
  };
  genres: string[] = [
    'Fiction',
    'Non-Fiction',
    'Mystery',
    'Thriller',
    'Romance',
    'Science Fiction',
    'Fantasy',
    'Historical Fiction',
    'Horror',
    'Biography' 
  ];

  errorMessage: string = '';
  books: any[] = [];
  selectedFile: File | null = null;

  isDeleteBookModalOpen = false;
  isUpdateBookModalOpen = false;
  isAddBookModalOpen = false;

  constructor(private bookService: BookservicesService,private fb: FormBuilder) {
  }

  ngOnInit(): void {
    this.fetchBooks();
  }

  openAddBookModal() {
    this.isAddBookModalOpen = true;
  }

  openDeleteBookModal(bookId: string, title: string) {
    this.deletebook.title = title;
    this.deletebook.book_id = bookId; 
    this.isDeleteBookModalOpen = true;
  }
  
  openUpdateBookModal(title: string) {
    this.isUpdateBookModalOpen = true;
    this.updatebook.title = title;
    this.fetchBookDetails(title); 
  }
  

  closeAddModal() {
    this.isAddBookModalOpen = false;
  }

  closeDeleteModal() {
    this.isDeleteBookModalOpen = false;
  }

  closeUpdateModal() {
    this.isUpdateBookModalOpen = false;
  }

  validateNumberInput(event: KeyboardEvent): void {
    const key = event.key;
    if (!/[0-9.]/.test(key) && key !== 'Backspace' && key !== 'Tab' && key !== 'Enter') {
      event.preventDefault();
    }
  }

  updateBookCount(): void {
    const totalBooksElement = document.querySelector('#totalBooks') as HTMLElement;
    totalBooksElement.textContent = this.books.length.toString();
  }

  fetchBookDetails(title: string): void {
    this.bookService.bookDetailsByTitle(title).subscribe(
      (data: any) => {
        this.updatebook.currentTitle = data.title;
        this.updatebook.title = data.title;
        this.updatebook.author_name = data.author_name;
        this.updatebook.genre_name = data.genre_name;
        this.updatebook.price = data.price;
        this.updatebook.stock = data.stock;
        this.updatebook.published_date = data.published_date;
        this.updatebook.description = data.description;
        this.updatebook.isbn = data.isbn;
        this.updatebook.rating = data.rating;
      },
      (error: any) => {
        console.error('Error fetching book details:', error);
        this.errorMessage = 'Failed to load book details. Please try again later.';
      }
    );
  }

  fetchBooks(): void {
    this.bookService.sellerbooks().subscribe(
      (data: any) => {
        this.books = data.books;
        this.updateBookTable();
        this.updateBookCount();
      },
      (error: any) => {
        console.error('Error fetching books:', error);
        this.errorMessage = 'Failed to load books. Please try again later.';
      }
    );
  }
  
  deleteBook(): void {
    if (!this.deletebook.book_id) {
        this.errorMessage = 'Book ID is required.';
        return;
    }

    this.bookService.deleteBook(this.deletebook.book_id ).subscribe(
        (response: any) => {
            if (response.message === 'Book Deleted successfully') {
                this.fetchBooks(); // Refresh the list of books
                this.closeDeleteModal(); // Close the delete modal
            }
        },
        (error: any) => { 
            // Handle different error statuses from the backend
            if (error?.status === 404 || error?.status === 400) {
                this.errorMessage = 'Failed: ' + error.error.message;
            } else {
                this.errorMessage = 'An error occurred during operation. Please try again.';
            }
        }
    );
  }

  onFileChange(event: any) {
    this.selectedFile = event.target.files[0];
  }

  addBook() {
    const formData = new FormData();
  
    // Validate required fields
    if (!this.newBook.title || !this.newBook.author_name || !this.newBook.genre_name || 
        this.newBook.price === undefined || this.newBook.stock === undefined || 
        !this.newBook.published_date || !this.newBook.description || !this.newBook.isbn ||
        this.newBook.rating === undefined) {
      this.errorMessage = 'Please fill in all fields before submitting.';
      return;
    }
  
    // Ensure a file is selected
    if (this.selectedFile) {
      formData.append('file', this.selectedFile, this.selectedFile.name);
    } else {
      this.errorMessage = 'Please select a file to upload.';
      return;
    }
  
    // Append other form data
    formData.append('title', this.newBook.title);
    formData.append('author_name', this.newBook.author_name);
    formData.append('genre_name', this.newBook.genre_name);
    formData.append('price', this.newBook.price.toString());
    formData.append('stock', this.newBook.stock.toString());
    formData.append('published_date', this.newBook.published_date);
    formData.append('description', this.newBook.description);
    formData.append('isbn', this.newBook.isbn);
    formData.append('rating', this.newBook.rating.toString());
  
    // Call the service to add the book
    this.bookService.addBook(formData).subscribe(
      (response) => {
        console.log('Book added successfully:', response);
        this.fetchBooks();  // Refresh the books list
  
        // Reset form and state
        this.closeAddModal();
        this.newBook = { 
          title: '', author_name: '', genre_name: '', price: null, 
          stock: null, published_date: '', description: '', isbn: '', rating: null 
        };
        this.selectedFile = null;
        this.errorMessage = '';  // Clear error message
      },
      (error) => {
        console.error('Error adding book:', error);
  
        // Handle the error based on the response
        if (error.status === 400) {
          this.errorMessage = 'Please check the form data and try again.';
        } else if (error.status === 500) {
          this.errorMessage = 'There was a problem with the server. Please try again later.';
        } else {
          this.errorMessage = 'An unexpected error occurred. Please try again.';
        }
      }
    );
  }
  
  updateBook(): void {
    const updatedFields: any = {};
  
    // Check if any fields are provided for updating
    if (this.updatebook.title) {
      updatedFields.title = this.updatebook.title;
    }
  
    // Loop through each field and check if the field has been changed or is not empty
    Object.keys(this.updatebook).forEach(key => {
      if (this.updatebook[key] !== '' && this.updatebook[key] !== null && this.updatebook[key] !== undefined) {
        updatedFields[key] = this.updatebook[key];
      }
    });
  
    // Validate that at least one field is updated
    if (Object.keys(updatedFields).length === 0) {
      this.errorMessage = 'No changes made. Please update at least one field.';
      return;
    }
  
    // Call the updateBook method in the service
    this.bookService.updateBook(updatedFields).subscribe(
      (response: any) => {
        alert(response.message);
        if (response.message === 'Book updated successfully') {
          this.fetchBooks(); // Refresh the list of books
          this.closeUpdateModal(); // Close the update modal
        }
      },
      (error: any) => {
        // Error handling for different HTTP status codes
        if (error?.status === 404) {
          this.errorMessage = 'Book not found. Please check the book ID and try again.';
        } else if (error?.status === 400) {
          this.errorMessage = 'Failed: ' + error.error.message;
        } else {
          this.errorMessage = 'An error occurred during operation. Please try again later.';
        }
      }
    );
  }
  
  updateBookTable(): void {
    const bookTableBody = document.querySelector('#listbooks') as HTMLTableSectionElement;
    bookTableBody.innerHTML = this.books.map(book => `
      <tr>
        <td>${book.title}</td>
        <td>${book.author_name}</td>
        <td>${book.genre_name}</td>
        <td>${book.published_date ? book.published_date : 'N/A'}</td>
      </tr>
    `).join('');
  }
}
