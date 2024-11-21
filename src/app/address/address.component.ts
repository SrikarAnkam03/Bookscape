import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-address',
  templateUrl: './address.component.html',
  styleUrls: ['./address.component.css']
})
export class AddressComponent implements OnInit {
  addresses: any[] = [];
  userId: string | null = localStorage.getItem('userId')
  addressId: string | null = '';
  isDeleteModal = false;
  isEditModal = false;
  isAddModal = false; 
  newAddress: any = {
    recipient_name: '',
    address: '',
    address_type: 'Home'  
  };
  editAddressData: any = {}; 
  apiUrlAddress: string = `http://127.0.0.1:5000/address`;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.getUserIdFromLocalStorage();
    if (this.userId) {
      this.fetchAddresses();
    }
  }

  getUserIdFromLocalStorage(): void {
    this.userId = localStorage.getItem('userId');
  }

  fetchAddresses(): void {
    const user_id = localStorage.getItem('userId')

    this.http.get<any[]>(`${this.apiUrlAddress}?user_id=${user_id}`, {headers: this.getAuthHeaders()}).subscribe(
      (response) => {
        this.addresses = response;
      },
      (error) => {
        console.error('Error fetching addresses:', error);
      }
    );
  }

  openAddModal(): void {
    this.isAddModal = true;
    this.newAddress = { recipient_name: '', address: '', address_type: 'Home' }; 
  }

  closeAddModal(): void {
    this.isAddModal = false;
  }

  addAddress(): void {
    if (this.userId) {
        const { recipient_name, address, address_type } = this.newAddress; 
        const addressData = { recipient_name, address, address_type }; 

        this.http.post(this.apiUrlAddress, addressData, { headers: this.getAuthHeaders() }).subscribe(
            (response) => {
                console.log('Address added:', response);
                this.fetchAddresses();
                this.closeAddModal();
            },
            (error) => {
                console.error('Error adding address:', error);
            }
        );
    }
  }

  openEditModal(addressId: string): void {
    const address = this.addresses.find(addr => addr.address_id === addressId);
    if (address) {
      this.isEditModal = true;
      this.editAddressData = { ...address }; 
    }
    console.log("🚀 ~ AddressComponent ~ openEditModal ~ this.editAddressData:", this.editAddressData)
  }
  
  closeEditModal(): void {
    this.isEditModal = false;
    this.editAddressData = {}; 
  }

  updateAddress(): void {
        if (this.editAddressData && this.editAddressData.address_id) {
        this.http.put(`${this.apiUrlAddress}`, this.editAddressData, { headers: this.getAuthHeaders() }).subscribe(
            (response) => {
              console.log(this.editAddressData)
                console.log('Address updated:', response);
                this.fetchAddresses(); 
                this.closeEditModal(); 
            },
            (error) => {
                console.error('Error updating address:', error);
            }
        );
    }
  }

  openRemoveModal(addressId: string): void {
    this.addressId = addressId;
    this.isDeleteModal = true;
  }

  closeModal(): void {
    this.isDeleteModal = false;
    this.addressId = null;
  }

  deleteAddress(): void {
    if (this.addressId) {
      this.http.delete(`${this.apiUrlAddress}?address_id=${this.addressId}`, { headers: this.getAuthHeaders() }).subscribe(
        () => {
          this.addresses = this.addresses.filter(addr => addr.address_id !== this.addressId);
          this.closeModal();
        },
        (error) => {
          console.error('Error deleting address:', error);
          this.closeModal();
        }
      );
    }
  }

  logAddressType(type: string): void {
    console.log('Selected address type:', type);
    console.log('Selected address type:', this.newAddress);
    this.newAddress.address_type = type
  }

  logAddress(type: string): void {
    console.log('Selected address type:', type);
    this.editAddressData.address_type = type
    console.log('Selected address type:', this.editAddressData.address_type);
  }

  getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    });
  }
}


