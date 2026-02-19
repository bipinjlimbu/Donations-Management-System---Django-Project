from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from ..models import DonorProfile, NGOProfile, Register

def home_view(request):
    return render(request,"main/home_page.html")

User = get_user_model()
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    section = request.GET.get('section', 'user-list')
    
    context = {
        'section': section,
        # Badge counts (Real counts from DB)
        'signup_count': Register.objects.filter(status='PENDING').count(),
        'campaign_count': 5, # Replace with CampaignRequest.objects.filter(is_approved=False).count()
    }

    # Data Fetching Logic
    if section == 'user-list':
        context['data_list'] = User.objects.all().order_by('-date_joined')
        
    elif section == 'signup-requests':
        context['signup_requests'] = Register.objects.filter(status='PENDING')
        
    elif section == 'profile-changes':
        # context['data_list'] = ProfileChange.objects.filter(is_reviewed=False)
        context['data_list'] = [] # Dummy placeholder
        
    elif section == 'campaign-requests':
        # context['data_list'] = CampaignRequest.objects.all()
        context['data_list'] = [] # Dummy placeholder

    return render(request, 'main/admin_dashboard.html', context)

@login_required
def approve_signup_request(request, request_id):
    if request.method == "POST":
        try:
            signup_request = Register.objects.get(id=request_id, status='PENDING')
            User.objects.create_user(
                username=signup_request.username,
                email=signup_request.email,
                password=signup_request.password,
                role=signup_request.role,
                phone=signup_request.phone,
                address=signup_request.address,
                profile_image=signup_request.profile_image,
            )
            
            if signup_request.role == "NGO":
                NGOProfile.objects.create(
                    user=User.objects.get(username=signup_request.username),
                    organization_name=signup_request.name,
                    registration_number=signup_request.registration_number,
                    verification_document=signup_request.verification_document
                )
            else:
                DonorProfile.objects.create(
                    user=User.objects.get(username=signup_request.username),
                    full_name=signup_request.name,
                    citizenship_number=signup_request.citizenship_number,
                    verification_document=signup_request.verification_document
                )
                
            signup_request.delete()
            messages.success(request, f"Signup request for {signup_request.username} has been approved.")
        except Register.DoesNotExist:
            messages.error(request, "Signup request not found or already processed.")
    
    return redirect("admin-dashboard")

@login_required
def reject_signup_request(request, request_id):
    if request.method == "POST":
        try:
            signup_request = Register.objects.get(id=request_id, status='PENDING')
            signup_request.delete()
            messages.success(request, f"Signup request for {signup_request.username} has been rejected.")
        except Register.DoesNotExist:
            messages.error(request, "Signup request not found or already processed.")
    
    return redirect("admin-dashboard")