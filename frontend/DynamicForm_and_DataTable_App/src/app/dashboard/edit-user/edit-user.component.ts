import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-edit-user',
  standalone: true,
  templateUrl: './edit-user.component.html',
  styleUrls: ['./edit-user.component.scss'],
  imports: [CommonModule, RouterModule, ReactiveFormsModule]
})
export class EditUserComponent implements OnInit {
  editForm!: FormGroup;
  userId!: number;
  selectedFile: File | null = null;
  previewUrl: string | ArrayBuffer | null = null;
  error: string = '';
  success: string = '';
  loading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userId = Number(this.route.snapshot.paramMap.get('user_id'));
    this.initForm();
    this.fetchUserData();
  }

  initForm(): void {
    this.editForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      uid: ['', [Validators.required, Validators.pattern(/^\d{11}$/)]],
      phone: ['', [Validators.required, Validators.pattern(/^\d{10}$/)]],
      address: [''],
      height: [''],
      weight: [''],
      blood_group: [''],
      emergency_contact: ['', [Validators.required, Validators.pattern(/^\d{10}$/)]],
      allergies: [''],
      notes: [''],
      profile_picture: ['']
    });
  }

  fetchUserData(): void {
    this.loading = true;
    this.http.get<any>(`http://127.0.0.1:5000/user/${this.userId}/dashboard`).subscribe({
      next: (data) => {
        this.editForm.patchValue({
          name: data.name,
          email: data.email,
          uid: data.uid,
          phone: data.phone,
          address: data.address || '',
          height: data.height || '',
          weight: data.weight || '',
          blood_group: data.blood_group || '',
          emergency_contact: data.emergency_contact,
          allergies: data.allergies || '',
          notes: data.notes || ''
        });
        
        if (data.profile_picture) {
          this.previewUrl = data.profile_picture;
        }
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Failed to load user data.';
        this.loading = false;
        console.error('Error fetching user data:', error);
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      if (!allowedTypes.includes(file.type)) {
        this.error = 'Only JPG, JPEG and PNG files are allowed.';
        return;
      }
      
      // Validate file size (max 2MB)
      if (file.size > 2 * 1024 * 1024) {
        this.error = 'File size should not exceed 2MB.';
        return;
      }
      
      this.selectedFile = file;
      this.error = ''; // Clear any previous errors
      
      // Create preview
      const reader = new FileReader();
      reader.onload = () => {
        this.previewUrl = reader.result;
      };
      reader.readAsDataURL(file);
    }
  }

  onImageError(event: any): void {
    event.target.src = 'assets/default-profile.png';
  }

  onSubmit(): void {
    if (this.editForm.invalid) {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.editForm.controls).forEach(key => {
        const control = this.editForm.get(key);
        control?.markAsTouched();
      });
      this.error = 'Please correct the errors in the form.';
      return;
    }

    const formData = new FormData();
    // Add all form fields to FormData
    Object.entries(this.editForm.value).forEach(([key, value]) => {
      if (value !== null && value !== undefined && key !== 'profile_picture') {
        formData.append(key, String(value));
      }
    });

    // Add profile picture if selected
    if (this.selectedFile) {
      formData.append('profile_picture', this.selectedFile);
    }

    this.loading = true;
    this.http.post<any>(`http://127.0.0.1:5000/user/${this.userId}/dashboard/edit`, formData).subscribe({
      next: (response) => {
        this.success = 'Profile updated successfully!';
        this.error = '';
        this.loading = false;
        // Redirect after short delay to show success message
        setTimeout(() => {
          this.router.navigate(['/user', this.userId, 'dashboard']);
        }, 1500);
      },
      error: (error: HttpErrorResponse) => {
        this.error = error.error?.message || 'Error updating profile.';
        this.success = '';
        this.loading = false;
        console.error('Error updating profile:', error);
      }
    });
  }

  backToDashboard(): void {
    this.router.navigate(['/user', this.userId, 'dashboard']);
  }
}