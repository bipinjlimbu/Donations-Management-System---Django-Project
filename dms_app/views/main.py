from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from ..models import Donation, DonorProfile, Feedback, NGOProfile, Register, Campaign
import re

def home_view(request):
    return render(request,"main/home_page.html")

def contact_view(request):
    errors = {}
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        
        if not name:
            errors["name"] = "Name is required."
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            errors["email"] = "Email is required."
        elif not re.match(email_pattern, email):
            errors["email"] = "Invalid email format."
        
        if not message:
            errors["message"] = "Message is required."
        
        if not errors:
            Feedback.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            messages.success(request, "Your feedback has been submitted successfully!")
            return redirect("contact")
        
    return render(request,"main/contact_page.html", {"errors": errors,"data": request.POST})

def about_view(request):
    return render(request,"main/about_page.html")

User = get_user_model()
@user_passes_test(lambda u: u.role == 'ADMIN')
def admin_dashboard_view(request):
    
    section = request.GET.get('section', 'user-list')
    
    pending_ngo_count = NGOProfile.objects.filter(pending_status="PENDING").count()
    pending_donor_count = DonorProfile.objects.filter(pending_status="PENDING").count()
    
    context = {
        'section': section,
        'signup_request_count': Register.objects.filter().count(),
        'campaign_request_count': Campaign.objects.filter(status=Campaign.Status.PENDING).count(),
        'pending_changes_count': pending_ngo_count + pending_donor_count,
    }

    if section == 'user-list':
        context['users'] = User.objects.all().order_by('-date_joined')
        
    elif section == 'signup-requests':
        context['signup_requests'] = Register.objects.all().order_by('-requested_at')
        
    elif section == 'profile-changes':
        donor_pending = DonorProfile.objects.filter(pending_status="PENDING").select_related('user')
        ngo_pending = NGOProfile.objects.filter(pending_status="PENDING").select_related('user')
        combined = list(donor_pending) + list(ngo_pending)
        combined.sort(key=lambda x: x.changes_requested_at, reverse=True)
        context['pending_changes'] = combined
        
    elif section == 'campaign-list':
        campaigns = Campaign.objects.exclude(status=Campaign.Status.PENDING).order_by('-approved_at')
        for campaign in campaigns:
            campaign.is_active = Campaign.is_active(campaign)
            campaign.is_completed = Campaign.is_completed(campaign)
            
        context['campaigns'] = campaigns
        

    elif section == 'campaign-requests':
        context['campaign_requests'] = Campaign.objects.filter(status=Campaign.Status.PENDING).order_by('-requested_at')
        
    return render(request, 'main/admin_dashboard.html', context)

@user_passes_test(lambda u: u.role == 'ADMIN')
def approve_signup_request(request, request_id):
    if request.method == "POST":
        try:
            signup_request = Register.objects.get(id=request_id)
            User.objects.create_user(
                username=signup_request.username,
                email=signup_request.email,
                password=signup_request.password,
                role=signup_request.role,
                phone=signup_request.phone,
                address=signup_request.address,
                profile_image=signup_request.profile_image,
            )
            
            if signup_request.role == "NGO":
                NGOProfile.objects.create(
                    user=User.objects.get(username=signup_request.username),
                    organization_name=signup_request.name,
                    registration_number=signup_request.registration_number,
                    verification_document=signup_request.verification_document
                )
            else:
                DonorProfile.objects.create(
                    user=User.objects.get(username=signup_request.username),
                    full_name=signup_request.name,
                    citizenship_number=signup_request.citizenship_number,
                    verification_document=signup_request.verification_document
                )
                
            signup_request.delete()
            messages.success(request, f"Signup request for {signup_request.username} has been approved.")
        except Register.DoesNotExist:
            messages.error(request, "Signup request not found or already processed.")
    
    return redirect("admin-dashboard")

@user_passes_test(lambda u: u.role == 'ADMIN')
def reject_signup_request(request, request_id):
    if request.method == "POST":
        try:
            signup_request = Register.objects.get(id=request_id)
            signup_request.delete()
            messages.success(request, f"Signup request for {signup_request.username} has been rejected.")
        except Register.DoesNotExist:
            messages.error(request, "Signup request not found or already processed.")
    
    return redirect("admin-dashboard")

def donate_view(request, campaign_id):
    if request.method == "POST":
        campaign = Campaign.objects.get(id=campaign_id)
        quantity = request.POST.get("quantity").strip()
        
        if not quantity.isdigit() or int(quantity) <= 0:
            messages.error(request, "Please enter a valid donation amount.")
            return redirect("campaigns")
        
        Donation.objects.create(
            donor=request.user,
            donor_name=request.user.donor_profile.full_name,
            campaign=campaign,
            campaign_title=campaign.title,
            ngo_name=campaign.ngo.organization_name,
            quantity=quantity,
            status = Donation.Status.PENDING
        )
        messages.success(request, "Your donation has been submitted successfully.")

    return redirect("campaigns")