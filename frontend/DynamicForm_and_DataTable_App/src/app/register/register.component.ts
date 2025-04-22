import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { NavbarComponent } from '../navbar/navbar.component';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule, NavbarComponent]
})
export class RegisterComponent implements OnInit {
  registerForm!: FormGroup;
  errorMessage: string = '';
  loading: boolean = false;
  selectedFile: File | null = null;
  
  // Add validation error flags
  validationErrors: { [key: string]: string } = {};

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.registerForm = this.formBuilder.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      uid: ['', [Validators.required, Validators.pattern('^[0-9]{11}$')]],
      phone: ['', [Validators.required, Validators.pattern('^[0-9]{10}$')]],
      address: [''],
      height: [''],
      weight: [''],
      blood_group: [''],
      emergency_contact: ['', [Validators.required, Validators.pattern('^[0-9]{10}$')]],
      allergies: [''],
      notes: [''],
      profile_picture: ['']
    });

    // Check if user is already logged in
    if (this.authService.getCurrentUser()) {
      this.router.navigate(['/dashboard']);
    }
  }

  onFileChange(event: any): void {
    if (event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
    }
  }

  validateField(fieldName: string, errorMessage: string): boolean {
    const control = this.registerForm.get(fieldName);
    if (control?.invalid && (control.dirty || control.touched)) {
      this.validationErrors[fieldName] = errorMessage;
      return false;
    }
    delete this.validationErrors[fieldName];
    return true;
  }

  validateForm(): boolean {
    let isValid = true;
    
    // Validate required fields
    if (!this.validateField('name', 'Name is required')) isValid = false;
    if (!this.validateField('email', 'Valid email is required')) isValid = false;
    if (!this.validateField('password', 'Password is required')) isValid = false;
    
    // Validate phone number - must be 10 digits
    if (!this.validateField('phone', 'Phone number must be exactly 10 digits')) isValid = false;
    
    // Validate UID - must be 11 digits
    if (!this.validateField('uid', 'UID must be exactly 11 digits')) isValid = false;
    
    // Validate emergency contact - must be 10 digits
    if (!this.validateField('emergency_contact', 'Emergency contact must be exactly 10 digits')) isValid = false;
    
    return isValid;
  }

  onSubmit(): void {
    // Mark all fields as touched to trigger validation
    Object.keys(this.registerForm.controls).forEach(key => {
      const control = this.registerForm.get(key);
      control?.markAsTouched();
    });

    if (this.registerForm.invalid) {
      this.validateForm();
      this.errorMessage = 'Please fix the errors in the form';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.validationErrors = {};

    // Create FormData for file upload
    const formData = new FormData();
    Object.keys(this.registerForm.value).forEach(key => {
      if (key !== 'profile_picture') {
        formData.append(key, this.registerForm.value[key]);
      }
    });

    if (this.selectedFile) {
      formData.append('profile_picture', this.selectedFile);
    }

    this.authService.register(formData).subscribe({
      next: (response) => {
        console.log('Registration successful:', response);
        this.router.navigate(['/login']);
      },
      error: (error) => {
        console.error('Registration error:', error);
        this.errorMessage = error.error?.message || 'Registration failed. Please try again.';
        this.loading = false;
      },
      complete: () => {
        this.loading = false;
      }
    });
  }
}