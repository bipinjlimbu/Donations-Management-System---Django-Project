from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ..models import Notification, Campaign, Donation, PendingProfile

@login_required
def ngo_dashboard_view(request):
    if request.user.role != 'NGO':
        messages.error(request, "You do not have permission to access the NGO dashboard.")
        return redirect("home")

    section = request.GET.get('section', 'campaign-list')
    current_status = request.GET.get('status', 'all')
    
    pending_ngo_count = PendingProfile.objects.filter(user=request.user,status=PendingProfile.Status.PENDING).count()
    pending_campaign_count = Campaign.objects.filter(ngo=request.user, status=Campaign.Status.PENDING).count()
    total_pending = pending_ngo_count + pending_campaign_count
    
    context = {
        'section': section,
        'current_status': current_status,
        'donation_request_count': Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.PENDING).count(),
        'pending_request_count': total_pending,
    }
    
    if section == 'campaign-list':
        campaigns = Campaign.objects.filter(ngo=request.user).exclude(status=Campaign.Status.PENDING).order_by('-approved_at')
        context['campaigns'] = campaigns
        
    elif section == 'my-donations' and current_status == 'all':
        context['donations'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name).exclude(status=Donation.Status.PENDING).order_by('-updated_at')
    elif section == 'my-donations' and current_status == 'delivered':
        context['donations'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.DELIVERED).order_by('-updated_at')
    elif section == 'my-donations' and current_status == 'rejected':
        context['donations'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.REJECTED).order_by('-updated_at')
        
    elif section == 'donation-requests':
        context['donation_requests'] = Donation.objects.filter(ngo_name=request.user.ngo_profile.organization_name, status=Donation.Status.PENDING).order_by('-requested_at')
        
    elif section == 'pending-requests':
        context['pending_campaigns'] = Campaign.objects.filter(ngo=request.user, status=Campaign.Status.PENDING).order_by('-requested_at')
        context['pending_profile_changes'] = PendingProfile.objects.filter(user=request.user, status=PendingProfile.Status.PENDING).order_by('-requested_at')
        
    return render(request, 'main/ngo_dashboard.html', context)

@login_required
def approve_donation_view(request, donation_id):
    if request.user.role != 'NGO':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    donation = Donation.objects.get(id=donation_id)
    campaign = Campaign.objects.get(title=donation.campaign_title)
    
    if campaign.ngo != request.user:
        messages.error(request, "You do not have permission to approve this donation.")
        return redirect("dashboard/ngo/?section=donation-requests/")
    
    if campaign.is_completed():
        messages.error(request, "This campaign has already been completed. Cannot approve more donations.")
        return redirect("dashboard/ngo/?section=donation-requests/")
    
    campaign.collected_quantity += int(donation.quantity)
    campaign.save()
    donation.status = Donation.Status.DELIVERED
    donation.updated_at = timezone.now()
    donation.save()
    
    Notification.objects.create(
        user = donation.donor,
        message = f"Your donation for campaign '{donation.campaign_title}' has been approved and marked as delivered."
    )
    
    messages.success(request, f"Donation from {donation.donor_name} for campaign '{donation.campaign_title}' has been approved.")
    return redirect("dashboard/ngo/?section=donation-requests/")

@login_required
def reject_donation_view(request, donation_id):
    if request.user.role != 'NGO':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("home")

    donation = Donation.objects.get(id=donation_id)
    
    if donation.campaign.ngo != request.user:
        messages.error(request, "You do not have permission to reject this donation.")
        return redirect("dashboard/ngo/?section=donation-requests/")
    
    if donation.campaign.is_completed():
        messages.error(request, "This campaign has already been completed. Cannot reject donations.")
        return redirect("dashboard/ngo/?section=donation-requests/")

    donation.status = Donation.Status.REJECTED
    donation.updated_at = timezone.now()
    donation.save()
    
    Notification.objects.create(
        user = donation.donor,
        message = f"Your donation for campaign '{donation.campaign_title}' has been rejected."
    )
    
    messages.info(request, f"Donation from {donation.donor_name} for campaign '{donation.campaign_title}' has been rejected.")
    return redirect("dashboard/ngo/?section=donation-requests/")
