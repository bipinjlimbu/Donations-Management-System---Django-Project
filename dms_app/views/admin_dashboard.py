from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import NGOProfile, DonorProfile, Register, Campaign, Feedback, Donation, User

@login_required
def admin_dashboard_view(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to access the admin dashboard.")
        return redirect("home")
    
    section = request.GET.get('section', 'user-list')
    current_status = request.GET.get('status', 'all')
    
    pending_ngo_count = NGOProfile.objects.filter(pending_status="PENDING").count()
    pending_donor_count = DonorProfile.objects.filter(pending_status="PENDING").count()
    
    context = {
        'section': section,
        'current_status': current_status,
        'signup_request_count': Register.objects.filter().count(),
        'campaign_request_count': Campaign.objects.filter(status=Campaign.Status.PENDING).count(),
        'pending_changes_count': pending_ngo_count + pending_donor_count,
        'feedback_count': Feedback.objects.filter(status=Feedback.Status.UNREAD).count(),
    }

    if section == 'user-list':
        context['users'] = User.objects.all().order_by('-date_joined')
        
    elif section == 'signup-requests':
        context['signup_requests'] = Register.objects.all().order_by('-requested_at')
        
    elif section == 'profile-changes':
        donor_pending = DonorProfile.objects.filter(pending_status="PENDING").select_related('user')
        ngo_pending = NGOProfile.objects.filter(pending_status="PENDING").select_related('user')
        combined = list(donor_pending) + list(ngo_pending)
        combined.sort(key=lambda x: x.changes_requested_at, reverse=True)
        context['pending_changes'] = combined
        
    elif section == 'campaign-list':
        campaigns = Campaign.objects.exclude(status=Campaign.Status.PENDING).order_by('-approved_at')
        context['campaigns'] = campaigns
        
    elif section == 'donations' and current_status == 'all':
        context['donations'] = Donation.objects.exclude(status=Donation.Status.PENDING).order_by('-requested_at')
    elif section == 'donations' and current_status == 'delivered':
        context['donations'] = Donation.objects.filter(status=Donation.Status.DELIVERED).order_by('-requested_at')
    elif section == 'donations' and current_status == 'rejected':
        context['donations'] = Donation.objects.filter(status=Donation.Status.REJECTED).order_by('-requested_at')
        
    elif section == 'campaign-requests':
        context['campaign_requests'] = Campaign.objects.filter(status=Campaign.Status.PENDING).order_by('-requested_at')
        
    elif section == 'feedback':
        context['feedbacks'] = Feedback.objects.all().order_by('-submitted_at')
        
    return render(request, 'main/admin_dashboard.html', context)

@login_required
def approve_signup_request(request, request_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")
    
    if request.method == "POST":
        try:
            signup_request = Register.objects.get(id=request_id)
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
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    if request.method == "POST":
        try:
            signup_request = Register.objects.get(id=request_id)
            signup_request.delete()
            messages.success(request, f"Signup request for {signup_request.username} has been rejected.")
        except Register.DoesNotExist:
            messages.error(request, "Signup request not found or already processed.")
    
    return redirect("admin-dashboard")

@login_required
def mark_feedback_toggle(request, feedback_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    try:
        feedback = Feedback.objects.get(id=feedback_id)
        if feedback.status == Feedback.Status.UNREAD:
            feedback.status = Feedback.Status.READ
        else:
            feedback.status = Feedback.Status.UNREAD
        feedback.save()
        messages.success(request, f"Feedback from {feedback.user.username} has been marked as read.")
    except Feedback.DoesNotExist:
        messages.error(request, "Feedback not found or already processed.")
    
    return redirect("admin-dashboard")

@login_required
def delete_feedback_view(request, feedback_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.delete()
        messages.success(request, f"Feedback from {feedback.user.username} has been deleted.")
    except Feedback.DoesNotExist:
        messages.error(request, "Feedback not found or already processed.")
    
    return redirect("admin-dashboard")