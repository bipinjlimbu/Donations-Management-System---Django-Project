from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from ..models import User, Donation, DonorProfile, Feedback, NGOProfile, Register, Campaign
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

@login_required
def donate_view(request, campaign_id):
    if request.user.role != 'DONOR':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

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
            ngo_name=campaign.ngo.ngo_profile.organization_name,
            quantity=quantity,
            item_type=campaign.item_type,
            unit=campaign.unit,
            status = Donation.Status.PENDING
        )
        messages.success(request, "Your donation has been submitted successfully.")

    return redirect("campaigns")

@login_required
def ngo_dashboard_view(request):
    if request.user.role != 'NGO':
        messages.error(request, "You do not have permission to access the NGO dashboard.")
        return redirect("home")

    section = request.GET.get('section', 'campaign-list')
    current_status = request.GET.get('status', 'all')
    
    pending_ngo_count = NGOProfile.objects.filter(pending_status="PENDING").count()
    pending_campaign_count = Campaign.objects.filter(ngo=request.user, status=Campaign.Status.PENDING).count()
    total_pending = pending_ngo_count + pending_campaign_count
    
    context = {
        'section': section,
        'current_status': current_status,
        'donation_request_count': Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.PENDING).count(),
        'pending_request_count': total_pending,
    }
    
    if section == 'campaign-list':
        campaigns = Campaign.objects.filter(ngo=request.user).exclude(status=Campaign.Status.PENDING).order_by('-approved_at')
        for campaign in campaigns:
            campaign.is_active = Campaign.is_active(campaign)
            campaign.is_completed = Campaign.is_completed(campaign)
        context['campaigns'] = campaigns
        
    elif section == 'my-donations' and current_status == 'all':
        context['donations'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name).exclude(status=Donation.Status.PENDING).order_by('-updated_at')
    elif section == 'my-donations' and current_status == 'delivered':
        context['donations'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.DELIVERED).order_by('-updated_at')
    elif section == 'my-donations' and current_status == 'rejected':
        context['donations'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.REJECTED).order_by('-updated_at')
        
    elif section == 'donation-requests':
        context['donation_requests'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.PENDING).order_by('-requested_at')
        
    elif section == 'pending-requests':
        context['pending_campaigns'] = Campaign.objects.filter(ngo=request.user, status=Campaign.Status.PENDING).order_by('-requested_at')
        context['pending_profile_changes'] = NGOProfile.objects.filter(user=request.user, pending_status="PENDING").order_by('-changes_requested_at')
        
    return render(request, 'main/ngo_dashboard.html', context)

@login_required
def approve_donation_view(request, donation_id):
    if request.user.role != 'NGO':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    donation = Donation.objects.get(id=donation_id)
    campaign = Campaign.objects.get(title=donation.campaign_title)
    
    if campaign.ngo != request.user:
        messages.error(request, "You do not have permission to approve this donation.")
        return redirect("ngo-dashboard")
    
    if campaign.is_completed():
        messages.error(request, "This campaign has already been completed. Cannot approve more donations.")
        return redirect("ngo-dashboard")
    
    campaign.collected_quantity += int(donation.quantity)
    campaign.save()
    donation.status = Donation.Status.DELIVERED
    donation.updated_at = timezone.now()
    donation.save()
    messages.success(request, f"Donation from {donation.donor_name} for campaign '{donation.campaign_title}' has been approved.")
    return redirect("ngo-dashboard")

@login_required
def reject_donation_view(request, donation_id):
    if request.user.role != 'NGO':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    donation = Donation.objects.get(id=donation_id)
    
    if donation.campaign.ngo != request.user:
        messages.error(request, "You do not have permission to reject this donation.")
        return redirect("ngo-dashboard")
    
    if donation.campaign.is_completed():
        messages.error(request, "This campaign has already been completed. Cannot reject donations.")
        return redirect("ngo-dashboard")

    donation.status = Donation.Status.REJECTED
    donation.updated_at = timezone.now()
    donation.save()
    messages.info(request, f"Donation from {donation.donor_name} for campaign '{donation.campaign_title}' has been rejected.")
    return redirect("ngo-dashboard")

@login_required
def donor_dashboard_view(request):
    section = request.GET.get('section', 'my-donations')
    current_status = request.GET.get('status', 'all')
    
    profile_change_count = DonorProfile.objects.filter(user=request.user, pending_status="PENDING").count()
    pending_donation_count = Donation.objects.filter(donor=request.user, status=Donation.Status.PENDING).count()
    total_pending = profile_change_count + pending_donation_count
    
    context = {
        'section': section,
        'current_status': current_status,
        'pending_requests_count': total_pending,
    }
    
    if section == 'my-donations' and current_status == 'all':
        context['donations'] = Donation.objects.filter(donor=request.user).exclude(status=Donation.Status.PENDING).order_by('-requested_at')
    elif section == 'my-donations' and current_status == 'delivered':
        context['donations'] = Donation.objects.filter(donor=request.user, status=Donation.Status.DELIVERED).order_by('-requested_at')
    elif section == 'my-donations' and current_status == 'rejected':
        context['donations'] = Donation.objects.filter(donor=request.user, status=Donation.Status.REJECTED).order_by('-requested_at')
    elif section == 'pending-requests':
        context['pending_donations'] = Donation.objects.filter(donor=request.user, status=Donation.Status.PENDING).order_by('-requested_at')
        context['pending_profile_changes'] = DonorProfile.objects.filter(user=request.user, pending_status="PENDING").order_by('-changes_requested_at')
        
    return render(request, 'main/donor_dashboard.html', context )