from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import User, NGOProfile, DonorProfile
import re

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'main/profile_page.html', {'user': user})

@login_required
def edit_profile_view(request, user_id):
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if user_to_edit.role == "NGO":
        ngo_profile, created = NGOProfile.objects.get_or_create(user=user_to_edit)
    else:
        donor_profile, created = DonorProfile.objects.get_or_create(user=user_to_edit)
    
    if request.user.id != user_id and request.user.role != 'ADMIN':
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
            return render(request, 'main/edit_profile_page.html', {'user_to_edit': user_to_edit, 'errors': errors})
        
        elif request.user.role == 'ADMIN':
            user_to_edit.username = username
            user_to_edit.email = email
            user_to_edit.phone = phone
            user_to_edit.address = address
            if image:
                user_to_edit.profile_image = image
            user_to_edit.save()
            
            if user_to_edit.role == "NGO":
                ngo_profile.organization_name = name
                ngo_profile.save()
            else:
                donor_profile.full_name = name
                donor_profile.save()
                
            messages.success(request, "Profile updated successfully.")
            return redirect('admin-dashboard')
        
        else:
            if user_to_edit.role == "NGO":
                ngo_profile.pending_username = username
                ngo_profile.pending_email = email
                ngo_profile.pending_phone = phone
                ngo_profile.pending_address = address
                if image:
                    ngo_profile.pending_image = image
                ngo_profile.pending_name = name
                ngo_profile.save()
            else:
                donor_profile.pending_username = username
                donor_profile.pending_email = email
                donor_profile.pending_phone = phone
                donor_profile.pending_address = address
                if image:
                    donor_profile.pending_image = image
                donor_profile.pending_name = name
                donor_profile.save()
            
            messages.success(request, "Profile update request submitted for admin approval.")
            return redirect('profile', user_id=user_id)
    
    return render(request, 'main/edit_profile_page.html', {'user_to_edit': user_to_edit})

def approve_pending_changes(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.role == "NGO":
        profile = get_object_or_404(NGOProfile, user=user)
    else:
        profile = get_object_or_404(DonorProfile, user=user)
    
    if profile.pending_status != "PENDING":
        messages.error(request, "No pending changes to approve.")
        return redirect('admin-dashboard')
    
    user.username = profile.pending_username
    user.email = profile.pending_email
    user.phone = profile.pending_phone
    user.address = profile.pending_address
    
    if user.role == "NGO":
        profile.organization_name = profile.pending_name
    else:
        profile.full_name = profile.pending_name
        
    if profile.pending_image:
        user.profile_image = profile.pending_image
        
    profile.pending_status = "APPROVED"
    profile.save()
    user.save()
    
    messages.success(request, "Pending changes approved successfully.")
    return redirect('admin-dashboard')

def reject_profile_changes(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.role == "NGO":
        profile = get_object_or_404(NGOProfile, user=user)
    else:
        profile = get_object_or_404(DonorProfile, user=user)
    
    if profile.pending_status != "PENDING":
        messages.error(request, "No pending changes to reject.")
        return redirect('admin-dashboard')
    
    profile.pending_status = "REJECTED"
    profile.save()
    
    messages.success(request, "Pending changes rejected.")
    return redirect('admin-dashboard')