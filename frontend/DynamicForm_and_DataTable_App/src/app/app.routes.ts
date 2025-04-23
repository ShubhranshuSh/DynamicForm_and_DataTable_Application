import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { UserDashboardComponent } from './dashboard/user-dashboard/user-dashboard.component';
import { authGuard } from './guards/auth.guard';
import { EditUserComponent } from './dashboard/edit-user/edit-user.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { 
    path: 'user/:id/dashboard', 
    component: UserDashboardComponent, 
    canActivate: [authGuard]
  },
  // Redirect old dashboard URL to prevent issues
  { 
    path: 'dashboard', 
    redirectTo: 'user/0/dashboard'  // Will be replaced with actual ID in guard
  },
  { path: 'user/:user_id/dashboard/edit', component: EditUserComponent },
];