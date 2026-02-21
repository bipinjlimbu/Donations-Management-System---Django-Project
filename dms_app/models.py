from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class ContactInfo(models.Model):
    phone = models.CharField(max_length=15)
    address = models.TextField()
    profile_image = models.ImageField(upload_to='images/profiles/', blank=True, null=True)
    
    class Meta:
        abstract = True

class PendingChanges(models.Model):
    pending_name = models.CharField(max_length=100, blank=True, null=True)
    pending_username = models.CharField(max_length=150, blank=True, null=True)
    pending_email = models.EmailField(blank=True, null=True)
    pending_phone = models.CharField(max_length=15, blank=True, null=True)
    pending_address = models.TextField(blank=True, null=True)
    pending_image = models.ImageField(upload_to='images/profiles/', blank=True, null=True)

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
    profile_image = models.ImageField(upload_to='images/profiles/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

class Register(ContactInfo):        
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=15, choices=User.Role.choices, default=User.Role.DONOR)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    citizenship_number = models.CharField(max_length=20, blank=True, null=True)
    verification_document = models.FileField(upload_to='images/verification_docs/')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class NGOProfile(PendingChanges):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ngo_profile')
    organization_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50)
    verification_document = models.FileField(upload_to='images/ngo_docs/', blank=True, null=True)

class DonorProfile(PendingChanges):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    full_name = models.CharField(max_length=100)
    citizenship_number = models.CharField(max_length=20)
    verification_document = models.FileField(upload_to='images/donor_docs/', blank=True, null=True)

class Campaign(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    campaign_image = models.ImageField(upload_to='images/campaigns/', blank=True, null=True)
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
    
    def is_active(self):
        today = now().date()
        return self.status == self.Status.APPROVED and self.start_date <= today <= self.end_date
    
    def is_completed(self):
        return self.status == self.Status.COMPLETED or (self.end_date < now().date() and self.collected_quantity >= self.target_quantity)

class Donation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DELIVERED = 'DELIVERED', 'Delivered'
        REJECTED = 'REJECTED', 'Rejected'
        
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, limit_choices_to={'role': User.Role.DONOR}, null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    delivered_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"