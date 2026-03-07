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