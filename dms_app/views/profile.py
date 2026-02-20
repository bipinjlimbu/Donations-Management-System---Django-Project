from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..models import User, NGOProfile, DonorProfile

@login_required
def edit_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'main/edit_profile_page.html', {'user': user})