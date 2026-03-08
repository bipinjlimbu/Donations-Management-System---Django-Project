from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from ..models import User, Donation, DonorProfile, Feedback, NGOProfile, Register, Campaign
import re

def home_view(request):
    context = {}
    
    campaigns = Campaign.objects.exclude(status__in=[Campaign.Status.PENDING, Campaign.Status.REJECTED]).order_by('-approved_at')[:3]
    for campaign in campaigns:
        campaign.is_active = Campaign.is_active(campaign)
        campaign.is_completed = Campaign.is_completed(campaign)
        
    context["campaigns"] = campaigns
    
    return render(request,"main/home_page.html", context)

def contact_view(request):
    errors = {}

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        
        if not message:
            errors["message"] = "Message is required."
        
        if not errors:
            Feedback.objects.create(
                user=request.user,
                subject=subject,
                message=message
            )
            
            messages.success(request, "Your feedback has been submitted successfully!")
            return redirect("contact")
        
    return render(request,"main/contact_page.html", {"errors": errors,"data": request.POST})

def about_view(request):
    return render(request,"main/about_page.html")