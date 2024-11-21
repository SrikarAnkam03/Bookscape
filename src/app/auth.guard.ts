import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, Router } from '@angular/router';
import { UserService } from './services/user.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {

  constructor(private userService: UserService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const expectedRole = route.data['role']; 
    const userRole = this.userService.role_name; 

    // Check if the user is authenticated
    if (!localStorage.getItem("access_token")) {
      this.router.navigate(['/login']); 
      return false;
    }

    // Check if the user's role matches the expected role
    if (userRole !== expectedRole) {
      localStorage.removeItem('access_token');
      localStorage.clear();
      this.router.navigate(['/login']);
      return false;
    }

    return true; 
  }
}
