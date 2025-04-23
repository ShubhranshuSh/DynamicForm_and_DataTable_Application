import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';


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

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userId = Number(this.route.snapshot.paramMap.get('user_id'));

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

    // For now, skip pre-filling. Will be added during integration
  }

  onSubmit(): void {
    if (this.editForm.invalid) return;
    console.log('Form submitted:', this.editForm.value);
  }
}
