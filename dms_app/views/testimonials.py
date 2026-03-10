from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Testimonial

def testimonials_view(request):
    return render(request, "main/testimonials_page.html")

def create_testimonial_view(request):
    errors = {}
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        content = request.POST.get("content", "").strip()
        
        if not content:
            errors["content"] = "Content cannot be empty."
        
        if errors:
            return render(request, "main/create_testimonial_page.html", {"errors": errors, "data": request.POST})
        
        Testimonial.objects.create(
            user=request.user,
            rating=rating,
            content=content
            status="PENDING"
        )
        messages.success(request, "Your testimonial has been submitted and is pending review.")
        return redirect("testimonials")
            
    return render(request, "main/create_testimonial_page.html")