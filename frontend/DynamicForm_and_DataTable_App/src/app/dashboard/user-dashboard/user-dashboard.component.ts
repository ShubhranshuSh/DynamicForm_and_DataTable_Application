import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

interface UserDetails {
  id: number;
  name: string;
  email: string;
  uid: string;
  phone: string;
  address?: string;
  height?: string;
  weight?: string;
  blood_group?: string;
  emergency_contact: string;
  allergies?: string;
  notes?: string;
  profile_picture?: string;
  roles: string[];
}

@Component({
  selector: 'app-user-dashboard',
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterModule]
})
export class UserDashboardComponent implements OnInit {
  userId: number = 0;
  userDetails: UserDetails | null = null;
  loading: boolean = true;
  error: string = '';
  
  constructor(
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    const user = this.authService.getCurrentUser();
    
    if (!user) {
      this.router.navigate(['/login']);
      return;
    }
    
    this.userId = user.id;
    
    // Check if we're on the correct URL
    this.route.paramMap.subscribe(params => {
      const urlId = parseInt(params.get('id') || '0', 10);
      
      // If URL doesn't match user ID, navigate to correct URL
      if (urlId !== this.userId) {
        this.router.navigate([`/user/${this.userId}/dashboard`]);
        return;
      }
      
      this.loadUserData();
    });
  }
  
  loadUserData(): void {
    this.loading = true;
    this.authService.getUserDashboard(this.userId).subscribe({
      next: (response) => {
        if (response && response.user) {
          this.userDetails = response.user;
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.message || 'Failed to load user data';
        this.loading = false;
        
        // If unauthorized, log out (token might be expired)
        if (err.status === 401 || err.status === 403) {
          this.authService.logout();
        }
      }
    });
  }
  
  logout(): void {
    this.authService.logout();
  }
  
  // Helper method to display file name from path
  getFileName(path: string | undefined): string {
    if (!path) return 'No file uploaded';
    const parts = path.split('/');
    return parts[parts.length - 1];
  }
}