import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
  standalone: true,
  imports: [RouterModule, CommonModule]
})
export class NavbarComponent implements OnInit {
  isLoggedIn: boolean = false;
  
  constructor(private authService: AuthService) {
    console.log('Navbar Component Loaded');
  }
  
  ngOnInit(): void {
    this.authService.isAuthenticated.subscribe(status => {
      this.isLoggedIn = status;
    });
  }
  
  logout(): void {
    this.authService.logout();
  }
}