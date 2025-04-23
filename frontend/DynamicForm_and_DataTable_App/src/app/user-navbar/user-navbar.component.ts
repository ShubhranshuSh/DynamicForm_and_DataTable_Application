import { Component, OnInit } from '@angular/core';
import { RouterModule, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-user-navbar',
  templateUrl: './user-navbar.component.html',
  styleUrls: ['./user-navbar.component.scss'],
  standalone: true,
  imports: [RouterModule, CommonModule]
})
export class UserNavbarComponent implements OnInit {
  isLoggedIn: boolean = false;
  userId: number | null = null;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    const user = this.authService.getCurrentUser();
    this.isLoggedIn = !!user;
    if (user) {
      this.userId = user.id;
    }
  }

  logout(): void {
    this.authService.logout();
  }

  navigateToEditProfile(): void {
    if (this.userId !== null) {
      this.router.navigate([`/user/${this.userId}/dashboard/edit`]);
    }
  }
}
