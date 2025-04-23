import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';

interface LoginResponse {
  token: string;
  email: string;
  role: string[];
  id: number;
}

interface RegisterResponse {
  message: string;
}

interface UserDetails {
  id: number;
  name: string;
  email: string;
  uid: string;
  phone: string;
  address: string;
  height: string;
  weight: string;
  blood_group: string;
  emergency_contact: string;
  allergies: string;
  notes: string;
  profile_picture: string;
  roles: string[];
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API_URL = 'http://localhost:5000'; // Adjust to your Flask backend URL
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isAuthenticated = this.isAuthenticatedSubject.asObservable();
  
  constructor(private http: HttpClient, private router: Router) {}
  
  // Add this method to expose API_URL
  getApiUrl(): string {
    return this.API_URL;
  }
  
  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.API_URL}/login`, { email, password })
      .pipe(
        tap(response => {
          localStorage.setItem('token', response.token);
          localStorage.setItem('user', JSON.stringify({
            email: response.email,
            role: response.role,
            id: response.id
          }));
          this.isAuthenticatedSubject.next(true);
        })
      );
  }
  
  register(formData: FormData): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.API_URL}/register`, formData);
  }
  
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }
  
  getCurrentUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
  
  getToken(): string | null {
    return localStorage.getItem('token');
  }
  
  getUserDashboard(userId: number): Observable<any> {
    return this.http.get(`${this.API_URL}/user/${userId}/dashboard`);
  }
  
  private hasToken(): boolean {
    return !!localStorage.getItem('token');
  }
}