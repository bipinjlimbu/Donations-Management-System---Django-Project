from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Testimonial, PendingTestimonial, Notification

def testimonials_view(request):
    testimonials = Testimonial.objects.filter(status=Testimonial.Status.APPROVED).order_by('-submitted_at')
    return render(request, "main/testimonials_page.html", {"testimonials": testimonials})

@login_required
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

@login_required 
def approve_testimonial_view(request, testimonial_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("testimonials")
    
    testimonial = Testimonial.objects.get(id=testimonial_id)
    testimonial.status = Testimonial.Status.APPROVED
    testimonial.save()
    
    Notification.objects.create(
        user = testimonial.user,
        message = "Your testimonial has been approved and is now visible on the site."
    )
    
    messages.success(request, "Testimonial approved successfully.")
    return redirect("/dashboard/admin/?section=testimonial-requests")

@login_required
def reject_testimonial_view(request, testimonial_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("testimonials")
    
    testimonial = Testimonial.objects.get(id=testimonial_id)
    testimonial.status = Testimonial.Status.REJECTED
    testimonial.save()
    
    Notification.objects.create(
        user = testimonial.user,
        message = "Your testimonial has been rejected."
    )
    
    messages.success(request, "Testimonial rejected successfully.")
    return redirect("/dashboard/admin/?section=testimonial-requests")

@login_required
def edit_testimonial_view(request, testimonial_id):  
    testimonial = Testimonial.objects.get(id=testimonial_id)
    if testimonial.user != request.user:
        messages.error(request, "You do not have permission to edit this testimonial.")
        return redirect("testimonials")
    
    errors = {}
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        message = request.POST.get("message", "").strip()
        
        if not message:
            errors["message"] = "Message cannot be empty."
        
        if errors:
            return render(request, "main/edit_testimonial_page.html", {"testimonial": testimonial, "errors": errors, "data": request.POST})
        
        if (
            str(testimonial.rating) == rating and
            testimonial.message == message
        ):
            messages.info(request, "No changes detected.")
            return redirect(f"/testimonials/edit/{testimonial.id}")
        
        PendingTestimonial.objects.create(
            testimonial = testimonial,
            rating = rating,
            message = message,
            status = Testimonial.Status.PENDING
        )
        messages.success(request, "Your testimonial has been updated and is pending review.")
        return redirect("testimonials")
    
    return render(request, "main/edit_testimonial_page.html", {"testimonial": testimonial, "errors": errors, "data": request.POST})

@login_required
def approve_testimonial_change(request, testimonial_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("testimonials")
    
    pending_testimonial = PendingTestimonial.objects.get(id=testimonial_id)
    testimonial = pending_testimonial.testimonial
    
    testimonial.rating = pending_testimonial.rating
    testimonial.message = pending_testimonial.message
    testimonial.save()
    
    pending_testimonial.status = PendingTestimonial.Status.APPROVED
    pending_testimonial.save()
    
    Notification.objects.create(
        user = testimonial.user,
        message = "Your testimonial changes have been approved."
    )
    
    messages.success(request,f"Changes for testimonial of {testimonial.user.username} have been approved.")
    return redirect("/dashboard/admin/?section=testimonial-changes")

@login_required
def reject_testimonial_change(request, testimonial_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("testimonials")
    
    pending_testimonial = PendingTestimonial.objects.get(testimonial_id)
    pending_testimonial.status = PendingTestimonial.Status.REJECTED
    pending_testimonial.save()
    
    Notification.objects.create(
        user = pending_testimonial.testimonial.user,
        message = "Your testimonial changes have been rejected."
    )
    
    messages.info(request,f"Changes for testimonial of {pending_testimonial.testimonial.user.username} have been rejected.")
    return redirect("/dashboard/admin/?section=testimonial-changes")
 
@login_required   
def delete_testimonial_view(request, testimonial_id):
    testimonial = Testimonial.objects.get(id=testimonial_id)
    if testimonial.user != request.user or request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to delete this testimonial.")
        return redirect("testimonials")
    
    testimonial.delete()
    messages.success(request, "Your testimonial has been deleted.")
    
    Notification.objects.create(
        user = testimonial.user,
        message = "Your testimonial has been deleted."
    )
    
    if request.user.role == 'ADMIN':
        return redirect("/dashboard/admin/?section=testimonial-list")
    else:
        return redirect("testimonials")