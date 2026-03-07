from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Donation, DonorProfile, Campaign

@login_required
def donor_dashboard_view(request):
    section = request.GET.get('section', 'my-donations')
    current_status = request.GET.get('status', 'all')
    
    profile_change_count = DonorProfile.objects.filter(user=request.user, pending_status="PENDING").count()
    pending_donation_count = Donation.objects.filter(donor=request.user, status=Donation.Status.PENDING).count()
    total_pending = profile_change_count + pending_donation_count
    
    context = {
        'section': section,
        'current_status': current_status,
        'pending_requests_count': total_pending,
    }
    
    if section == 'my-donations' and current_status == 'all':
        context['donations'] = Donation.objects.filter(donor=request.user).exclude(status=Donation.Status.PENDING).order_by('-requested_at')
    elif section == 'my-donations' and current_status == 'delivered':
        context['donations'] = Donation.objects.filter(donor=request.user, status=Donation.Status.DELIVERED).order_by('-requested_at')
    elif section == 'my-donations' and current_status == 'rejected':
        context['donations'] = Donation.objects.filter(donor=request.user, status=Donation.Status.REJECTED).order_by('-requested_at')
    elif section == 'pending-requests':
        context['pending_donations'] = Donation.objects.filter(donor=request.user, status=Donation.Status.PENDING).order_by('-requested_at')
        context['pending_profile_changes'] = DonorProfile.objects.filter(user=request.user, pending_status="PENDING").order_by('-changes_requested_at')
        
    return render(request, 'main/donor_dashboard.html', context )

@login_required
def donate_view(request, campaign_id):
    if request.user.role != 'DONOR':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    if request.method == "POST":
        campaign = Campaign.objects.get(id=campaign_id)
        quantity = request.POST.get("quantity").strip()
        
        if not quantity.isdigit() or int(quantity) <= 0:
            messages.error(request, "Please enter a valid donation amount.")
            return redirect("campaigns")
        
        Donation.objects.create(
            donor=request.user,
            donor_name=request.user.donor_profile.full_name,
            campaign=campaign,
            campaign_title=campaign.title,
            ngo_name=campaign.ngo.ngo_profile.organization_name,
            quantity=quantity,
            item_type=campaign.item_type,
            unit=campaign.unit,
            status = Donation.Status.PENDING
        )
        messages.success(request, "Your donation has been submitted successfully.")

    return redirect("campaigns")
