from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import User, NGOProfile, DonorProfile, PendingProfile
import re

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'main/profile_page.html', {'user': user})

@login_required
def edit_profile_view(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.user.id != user_id:
        messages.error(request, "You do not have permission to edit this profile.")
        return redirect('home')
    
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        phone = request.POST.get("phone").strip()
        address = request.POST.get("address").strip()
        image = request.FILES.get("profile_image")
        
        errors = {}
        
        username_pattern = r'^[A-Z]{1}[a-zA-Z]{1,}[0-9]{1,}$'
        
        if not username:
            errors["username"] = "Username is required."
        elif User.objects.filter(username=username).exclude(id=user_id).exists():
            errors["username"] = "Username already exists."
        elif not re.match(username_pattern, username):
            errors["username"] = "Username must start with an uppercase letter and end with at least 1 digits."
            
        if user_to_edit.role != "ADMIN" and not name:
            errors["name"] = "Name is required."
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            errors["email"] = "Email is required."
        elif User.objects.filter(email=email).exclude(id=user_id).exists():
            errors["email"] = "Email already exists."
        elif not re.match(email_pattern, email):
            errors["email"] = "Invalid email format."
                    
        phone_pattern = r'^[0-9]{9,15}$'
        if not phone:
            errors["phone"] = "Phone number is required."
        elif not re.match(phone_pattern, phone):
            errors["phone"] = "Invalid phone number format."
            
        if not address:
            errors["address"] = "Address is required."
                    
        if errors:
            return render(request, 'main/edit_profile_page.html', {'user_to_edit': user_to_edit, 'errors': errors, 'data': request.POST})
        
        elif user_to_edit.role == "ADMIN":
            user_to_edit.username = username
            user_to_edit.email = email
            user_to_edit.phone = phone
            user_to_edit.address = address
            
            if image:
                user_to_edit.profile_image = image
            
            user_to_edit.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile', user_id=user_id)
        
        else:
            PendingProfile.objects.create(
                user=user_to_edit,
                name=name,
                username=username,
                email=email,
                phone=phone,
                address=address,
                profile_image=image if image else user_to_edit.profile_image,
                status=PendingProfile.Status.PENDING
            )

            messages.success(request, "Profile update request submitted for admin approval.")
            return redirect('profile', user_id=user_id)

    return render(request, 'main/edit_profile_page.html', {'user_to_edit': user_to_edit, 'data': request.POST})

@login_required
def approve_profile_changes(request, profile_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('home')
    
    pending_profile = get_object_or_404(PendingProfile, id=profile_id)
    user = pending_profile.user
    
    user.username = pending_profile.username
    user.email = pending_profile.email
    user.phone = pending_profile.phone
    user.address = pending_profile.address
    
    if pending_profile.profile_image != user.profile_image:
        user.profile_image = pending_profile.profile_image
        
    user.save()
    
    if user.role == "NGO":
        profile = get_object_or_404(NGOProfile, user=user)
        profile.organization_name = pending_profile.name
        profile.save()
    else:
        profile = get_object_or_404(DonorProfile, user=user)
        profile.full_name = pending_profile.name
        profile.save()
        
    pending_profile.status = PendingProfile.Status.APPROVED
    pending_profile.save()
    
    messages.success(request, "Pending changes approved successfully.")
    return redirect('dashboard/admin/?section=profile-changes/')

@login_required
def reject_profile_changes(request, profile_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('home')
    
    pending_profile = get_object_or_404(PendingProfile, id=profile_id)
    pending_profile.status = PendingProfile.Status.REJECTED
    pending_profile.save()
    
    messages.success(request, "Pending changes rejected.")
    return redirect('dashboard/admin/?section=profile-changes/')