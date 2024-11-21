import { Component } from '@angular/core';
import { WalletService } from '../services/walletservices.service';

@Component({
  selector: 'app-wallet',
  templateUrl: './wallet.component.html',
  styleUrls: ['./wallet.component.css']
})
export class WalletComponent {
  balance: number = 0;
  transactions: any[] = [];
  depositAmount: number = 0;
  withdrawAmount: number = 0;
  depositmodal: boolean = false;
  withdrawmodal: boolean = false;

  currentPage: number = 1;
  itemsPerPage: number = 10;
  paginatedTransactions: any[] = [];
  totalPages: number = 0;

  constructor(private walletService: WalletService) {}

  ngOnInit() {
    this.getBalance();
    this.getTransactions();
  }

  getBalance() {
    this.walletService.getBalance().subscribe(
      (response: any) => {
        this.balance = response.balance;
      },
      (error: any) => {
        console.error('Error fetching balance:', error);
      }
    );
  }

  getTransactions() {
    this.walletService.getTransactions().subscribe(
      (response: any) => {
        this.transactions = response.transactions;
        this.calculateTotalPages();
        this.updatePaginatedTransactions();
      },
      (error: any) => {
        console.error('Error fetching transactions:', error);
      }
    );
  }

  calculateTotalPages(): void {
    this.totalPages = Math.ceil(this.transactions.length / this.itemsPerPage);
  }

  // Update the orders to display on the current page
  updatePaginatedTransactions(): void {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    this.paginatedTransactions = this.transactions.slice(startIndex, endIndex);
  }

  // Navigate to the next page
  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.updatePaginatedTransactions();
    }
  }

  // Navigate to the previous page
  prevPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.updatePaginatedTransactions();
    }
  }

  deposit() {
    if (this.depositAmount > 0) {
      this.walletService.deposit(this.depositAmount).subscribe(
        (response: any) => {
          this.balance += this.depositAmount; 
          this.closeModal('deposit');
          this.getBalance(); 
          this.getTransactions();
        }, 
        (error: any) => {
          console.error('Deposit failed:', error);
        }
      );
    }
  }

  withdraw() {
    if (this.withdrawAmount > 0 && this.withdrawAmount <= this.balance) {
        this.walletService.withdraw(this.withdrawAmount).subscribe(
            (response: any) => {
                this.balance -= this.withdrawAmount; 
                this.closeModal('withdraw'); 
                this.getBalance();
                this.getTransactions();
            }, 
            (error: any) => {
                console.error('Withdrawal failed:', error);
                alert(error.error.message || 'Withdrawal failed');
            }
        );
    } else {
        alert('Insufficient balance - ' + this.balance);
    }
  }

  openDepositModal() {
    this.depositmodal = true;
  }

  openWithdrawModal() {
    this.withdrawmodal = true;
  }

  closeModal(type: string) {
    if (type === 'deposit') {
      this.depositmodal = false;
      this.depositAmount = 0; 
    } else if (type === 'withdraw') {
      this.withdrawmodal = false; 
      this.withdrawAmount = 0; 
    }
  }

  onDepositInput(event: any) {
    const value = parseFloat(event.target.value);
    if (isNaN(value) || value < 0) {
      event.target.value = 0; 
      this.depositAmount = 0; 
    } else {
      this.depositAmount = value;
    }
  }

  onWithdrawInput(event: any) {
    const value = parseFloat(event.target.value);
    if (isNaN(value) || value < 0) {
      event.target.value = 0; 
      this.withdrawAmount = 0; 
    } else {
      this.withdrawAmount = value; 
    }
  }

  preventNonNumeric(event: KeyboardEvent): void {
    const validKeys = [
      'Backspace', 'Tab', 'ArrowLeft', 'ArrowRight', 'Enter', 'Escape'
    ];
    const isNumber = /^[0-9]+$/.test(event.key);
  
    // Allow only valid keys and numbers
    if (!isNumber && !validKeys.includes(event.key)) {
      event.preventDefault();
    }
  }
  
}
