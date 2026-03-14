from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Feedback, Campaign, Testimonial, Notification

def home_view(request):
    context = {}
    if request.user.is_authenticated:
        context["alert_notification"] = Notification.objects.filter(user=request.user, is_read=False).exists()
    else:
        context["alert_notification"] = False
    
    campaigns = Campaign.objects.exclude(status__in=[Campaign.Status.PENDING, Campaign.Status.REJECTED]).order_by('-approved_at')[:3]
    for campaign in campaigns:
        campaign.is_active = Campaign.is_active(campaign)
        campaign.is_completed = Campaign.is_completed(campaign)
        
    context["campaigns"] = campaigns
    
    testimonials = Testimonial.objects.filter(status=Testimonial.Status.APPROVED).order_by('-submitted_at')[:3]
    context["testimonials"] = testimonials

    return render(request,"main/home_page.html", context)

def contact_view(request):
    errors = {}
    if request.user.is_authenticated:
        alert_notification = Notification.objects.filter(user=request.user, is_read=False).exists()
    else:
        alert_notification = False

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
        
    return render(request,"main/contact_page.html", {"errors": errors,"data": request.POST, "alert_notification": alert_notification})

def about_view(request):
    if request.user.is_authenticated:
        alert_notification = Notification.objects.filter(user=request.user, is_read=False).exists()
    else:
        alert_notification = False
        
    alert_notification = Notification.objects.filter(user=request.user, is_read=False).exists()
    return render(request,"main/about_page.html", {"alert_notification": alert_notification})

@login_required
def notifications_view(request):
    alert_notification = Notification.objects.filter(user=request.user, is_read=False).exists()
    return render(request,"main/notifications_page.html", {"alert_notification": alert_notification})