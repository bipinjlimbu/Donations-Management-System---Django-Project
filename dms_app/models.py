from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class ContactInfo(models.Model):
    phone = models.CharField(max_length=15)
    address = models.TextField()
    profile_image = models.ImageField(upload_to='profiles/temp/', blank=True, null=True)
    
    class Meta:
        abstract = True

class PendingChanges(models.Model):
    pending_name = models.CharField(max_length=100, blank=True, null=True)
    pending_email = models.EmailField(blank=True, null=True)
    pending_phone = models.CharField(max_length=15, blank=True, null=True)
    pending_address = models.TextField(blank=True, null=True)
    pending_image = models.ImageField(upload_to='profiles/pending/', blank=True, null=True)

    class Meta:
        abstract = True

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        NGO = 'NGO', 'Ngo'
        DONOR = 'DONOR', 'Donor'
        
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.DONOR)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/users/', blank=True, null=True)

class Register(ContactInfo):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=15, choices=User.Role.choices, default=User.Role.DONOR)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    citizenship_number = models.CharField(max_length=20, blank=True, null=True)
    verification_document = models.FileField(upload_to='verification_docs/')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.role} ({self.status})"

class NGOProfile(PendingChanges):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ngo_profile')
    organization_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50)
    verification_document = models.FileField(upload_to='ngo_docs/', blank=True, null=True)

class DonorProfile(PendingChanges):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    full_name = models.CharField(max_length=100)
    citizenship_number = models.CharField(max_length=20)
    verification_document = models.FileField(upload_to='donor_docs/', blank=True, null=True)

class Campaign(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    campaign_image = models.ImageField(upload_to='campaigns/', blank=True, null=True) # Added campaign image
    ngo = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.NGO})
    category = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    target_quantity = models.PositiveIntegerField()
    collected_quantity = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress_percentage(self):
        if self.target_quantity > 0:
            return (self.collected_quantity / self.target_quantity) * 100
        return 0

# Donation model remains the same as it references Campaign and User