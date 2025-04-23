// src/app/guards/auth.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const user = authService.getCurrentUser();
  if (!user) {
    router.navigate(['/login']);
    return false;
  }
  
  // If trying to access someone else's dashboard or generic dashboard URL
  if (route.routeConfig?.path === 'user/:id/dashboard') {
    const requestedId = parseInt(route.paramMap.get('id') || '0', 10);
    
    // If URL doesn't match the user's ID, redirect to their correct dashboard
    if (requestedId !== user.id) {
      router.navigate([`/user/${user.id}/dashboard`]);
      return false;
    }
  }
  
  return true;
};