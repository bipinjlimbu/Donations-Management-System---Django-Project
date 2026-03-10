from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Testimonial

def testimonials_view(request):
    return render(request, "main/testimonials_page.html")

def create_testimonial_view(request):
    errors = {}
    
    if Testimonial.objects.filter(user=request.user).exclude(status=Testimonial.Status.REJECTED).exists():
        messages.error(request, "You have already submitted a testimonial.")
        return redirect("testimonials")
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        message = request.POST.get("message", "").strip()
        
        if not message:
            errors["message"] = "Message cannot be empty."
        
        if errors:
            return render(request, "main/create_testimonial_page.html", {"errors": errors, "data": request.POST})
        
        Testimonial.objects.create(
            user=request.user,
            rating=rating,
            message=message,
            status=Testimonial.Status.PENDING
        )
        messages.success(request, "Your testimonial has been submitted and is pending review.")
        return redirect("testimonials")
            
    return render(request, "main/create_testimonial_page.html")

def approve_testimonial_view(request, testimonial_id):
    testimonial = Testimonial.objects.get(id=testimonial_id)
    testimonial.status = Testimonial.Status.APPROVED
    testimonial.save()
    messages.success(request, "Testimonial approved successfully.")
    return redirect("dashboard/admin/?section=testimonial-requests")