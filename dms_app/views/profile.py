from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..models import User, NGOProfile, DonorProfile

@login_required
def edit_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == "POST":
        name = request.POST.get("name").strip()
        email = request.POST.get("email").strip()
        phone = request.POST.get("phone").strip()
        address = request.POST.get("address").strip()
        image = request.FILES.get("profile_image")
        
        errors = {}
        
        if not name:
            errors["name"] = "Name is required."
        
        if not email:
            errors["email"] = "Email is required."
        
        if errors:
            return render(request, 'main/edit_profile_page.html', {'user': user, 'errors': errors})
        
        user.name = name
        user.email = email
        user.phone = phone
        user.address = address
        if image:
            user.profile_image = image
        user.save()
        
        messages.success(request, "Profile updated successfully.")
        return redirect('edit-profile', user_id=user.id)
    
    return render(request, 'main/edit_profile_page.html', {'user': user})