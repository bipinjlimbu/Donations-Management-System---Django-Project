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
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        
    pending_name = models.CharField(max_length=100, blank=True, null=True)
    pending_username = models.CharField(max_length=150, blank=True, null=True)
    pending_email = models.EmailField(blank=True, null=True)
    pending_phone = models.CharField(max_length=15, blank=True, null=True)
    pending_address = models.TextField(blank=True, null=True)
    pending_image = models.ImageField(upload_to='images/profiles/', blank=True, null=True)
    pending_status = models.CharField(max_length=15, choices=Status.choices, default=Status.APPROVED)
    changes_requested_at = models.DateTimeField(auto_now_add=True)

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
        
    class Category(models.TextChoices):
        FOOD = 'FOOD', 'Food'
        CLOTHING = 'CLOTHING', 'Clothing'
        MEDICAL = 'MEDICAL', 'Medical Supplies'
        EDUCATION = 'EDUCATION', 'Educational Materials'
        OTHER = 'OTHER', 'Other'
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    campaign_image = models.ImageField(upload_to='images/campaigns/', blank=True, null=True)
    ngo = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.NGO})
    category = models.CharField(max_length=100, choices=Category.choices, default=Category.OTHER)
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
        active_condition = self.status == self.Status.APPROVED and self.start_date <= today <= self.end_date
        if active_condition and self.status != self.Status.ACTIVE:
            self.status = self.Status.ACTIVE
            self.save()
        
        return active_condition
    
    def is_completed(self):
        today = now().date()
        completed_condition = self.status in [self.Status.ACTIVE, self.Status.APPROVED] and (today > self.end_date or self.collected_quantity >= self.target_quantity)
        if completed_condition and self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED
            self.save()
            
        return completed_condition
    
class pendingCampaign(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        
    title = models.CharField(max_length=200)
    description = models.TextField()
    campaign_image = models.ImageField(upload_to='images/campaigns/', blank=True, null=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='pending_campaign')
    category = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    target_quantity = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
        
class Donation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        DELIVERED = 'DELIVERED', 'Delivered'
        REJECTED = 'REJECTED', 'Rejected'
        
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, limit_choices_to={'role': User.Role.DONOR}, null=True, blank=True)
    donor_name = models.CharField(max_length=100)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    campaign_title = models.CharField(max_length=200)
    ngo_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    item_type = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

class Feedback(models.Model):
    class Status(models.TextChoices):
        READ = 'READ', 'Read'
        UNREAD = 'UNREAD', 'Unread'
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNREAD)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
class Testimonial(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)