from datetime import date
from django.shortcuts import render, redirect
from ..models import Campaign, PendingCampaign
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def campaigns_page_view(request):
    campaigns = Campaign.objects.exclude(status__in=[Campaign.Status.REJECTED, Campaign.Status.PENDING]).order_by('-approved_at')
        
    category = request.GET.get("category", "all")
    status = request.GET.get("status", "all")
    
    for campaign in campaigns:
        campaign.is_active = Campaign.is_active(campaign)
        campaign.is_completed = Campaign.is_completed(campaign)
        
    if category != "all":
        campaigns = campaigns.filter(category=category)
        
    if status != "all":
        campaigns = campaigns.filter(status=status)
        
        
    return render(request,"main/campaigns_page.html", {"campaigns": campaigns})

@login_required
def create_campaign_view(request):
    
    if request.user.role == 'DONOR':
        messages.error(request, "You do not have permission to create a campaign.")
        return redirect("campaigns")
    
    errors = {}
    if request.method == "POST":
        title = request.POST.get("title").strip()
        description = request.POST.get("description").strip()
        campaign_image = request.FILES.get("campaign_image")
        ngo = request.user.ngo_profile
        category = request.POST.get("category")
        item_type = request.POST.get("item_type").strip()
        unit = request.POST.get("unit").strip()
        target_quantity = request.POST.get("target_quantity").strip()
        start_date = request.POST.get("start_date").strip()
        end_date = request.POST.get("end_date").strip()
        
        if not title:
            errors["title"] = "Title is required."
            
        if not description:
            errors["description"] = "Description is required."
            
        if not category:
            errors["category"] = "Category is required."
            
        if not item_type:
            errors["item_type"] = "Item type is required."
            
        if not unit:
            errors["unit"] = "Unit is required."
            
        if not target_quantity:
            errors["target_quantity"] = "Target quantity is required."
        elif not target_quantity.isdigit():
            errors["target_quantity"] = "Target quantity must be a positive integer."
        elif int(target_quantity) <= 0:
            errors["target_quantity"] = "Target quantity must be greater than zero."
        
        if not start_date:
            errors["start_date"] = "Start date is required."
        elif start_date < str(date.today()):
            errors["start_date"] = "Start date cannot be in the past."
            
        if not end_date:
            errors["end_date"] = "End date is required."
        elif end_date < start_date:
            errors["end_date"] = "End date must be after the start date."
        
        if errors:
            return render(request, "main/create_campaign_page.html", {"errors": errors,"data": request.POST})
        
        Campaign.objects.create(
            title = title,
            description = description,
            campaign_image = campaign_image,
            ngo = ngo.user,
            category = category,
            item_type = item_type,
            unit = unit,
            target_quantity = target_quantity,
            collected_quantity = 0,
            start_date = start_date,
            end_date = end_date,
            status = Campaign.Status.PENDING
        )
        
        messages.success(request, "Campaign created successfully and is pending approval.")
        return redirect("campaigns")
    return render(request,"main/create_campaign_page.html")

@login_required
def approve_campaign_request(request, campaign_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("campaigns")
    
    campaign = Campaign.objects.get(id=campaign_id)
    campaign.status = Campaign.Status.APPROVED
    campaign.approved_at = date.today()
    campaign.save()
    messages.success(request, f"Campaign '{campaign.title}' has been approved.")
    return redirect("/dashboard/admin/?section=campaign-requests/")

@login_required
def reject_campaign_request(request, campaign_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("campaigns")

    campaign = Campaign.objects.get(id=campaign_id)
    campaign.status = Campaign.Status.REJECTED
    campaign.save()
    messages.info(request, f"Campaign '{campaign.title}' has been rejected.")
    return redirect("/dashboard/admin/?section=campaign-requests/")

def single_campaign_page_view(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    
    if campaign.status in [Campaign.Status.PENDING, Campaign.Status.REJECTED]:
        messages.warning(request, "This campaign is not available for viewing.")
        return redirect("campaigns")

    return render(request,"main/single_campaign_page.html", {"campaign": campaign})

@login_required
def edit_campaign_view(request, campaign_id):
   
    campaign = Campaign.objects.get(id=campaign_id)
    
    if request.user != campaign.ngo:
        messages.error(request, "You do not have permission to edit a campaign.")
        return redirect("campaigns")
    
    if campaign.status == Campaign.Status.APPROVED and campaign.ngo.user != request.user:
        messages.error(request, "You do not have permission to edit this campaign.")
        return redirect("campaigns")
    
    errors = {}
    
    if request.method == "POST":
        title = request.POST.get("title").strip()
        description = request.POST.get("description").strip()
        campaign_image = request.FILES.get("campaign_image")
        category = request.POST.get("category")
        item_type = request.POST.get("item_type").strip()
        unit = request.POST.get("unit").strip()
        target_quantity = request.POST.get("target_quantity").strip()
        
        if campaign.status == Campaign.Status.APPROVED:
            start_date = request.POST.get("start_date").strip()
        else:
            end_date = request.POST.get("end_date").strip()
        
        if not title:
            errors["title"] = "Title is required."
            
        if not description:
            errors["description"] = "Description is required."
            
        if not category:
            errors["category"] = "Category is required."
            
        if not item_type:
            errors["item_type"] = "Item type is required."
            
        if not unit:
            errors["unit"] = "Unit is required."
            
        if not target_quantity:
            errors["target_quantity"] = "Target quantity is required."
        elif not target_quantity.isdigit():
            errors["target_quantity"] = "Target quantity must be a positive integer."
        elif int(target_quantity) <= 0:
            errors["target_quantity"] = "Target quantity must be greater than zero."
        
        
        if campaign.status == Campaign.Status.APPROVED:
            if not start_date:
                errors["start_date"] = "Start date is required."
            elif start_date < str(date.today()):
                errors["start_date"] = "Start date cannot be in the past."
        else:
            if not end_date:
                errors["end_date"] = "End date is required."
            elif end_date < str(campaign.start_date):
                errors["end_date"] = "End date must be after the start date."
        
        if errors:
            return render(request, "main/edit_campaign_page.html", {"errors": errors,"data": request.POST, "campaign": campaign})
        
        if (
            campaign.title == title and
            campaign.description == description and
            campaign.category == category and
            campaign.item_type == item_type and
            campaign.unit == unit and
            str(campaign.target_quantity) == target_quantity and
            ((campaign.status == Campaign.Status.APPROVED and str(campaign.start_date) == start_date) or (campaign.status != Campaign.Status.APPROVED and str(campaign.end_date) == end_date)) and
            not campaign_image
        ):
            messages.info(request, "No changes detected.")
            return redirect(f"/campaigns/edit/{campaign.id}")
        
        PendingCampaign.objects.create(
            title = title,
            description = description,
            campaign_image = campaign_image if campaign_image else campaign.campaign_image,
            category = category,
            item_type = item_type,
            unit = unit,
            target_quantity = target_quantity,
            start_date = start_date if campaign.status == Campaign.Status.APPROVED else None,
            end_date = end_date if campaign.status != Campaign.Status.APPROVED else None,
            campaign = campaign,
            status = PendingCampaign.Status.PENDING
        )
        
        messages.success(request, "Campaign Changes Sent for Approval.")
        return redirect("campaigns")
    
    return render(request,"main/edit_campaign_page.html", {"campaign": campaign})

@login_required
def approve_campaign_changes(request, campaign_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("campaigns")
    
    pending_campaign = PendingCampaign.objects.get(id=campaign_id)
    campaign = pending_campaign.campaign
    
    campaign.title = pending_campaign.title
    campaign.description = pending_campaign.description
    campaign.category = pending_campaign.category
    campaign.item_type = pending_campaign.item_type
    campaign.unit = pending_campaign.unit
    campaign.target_quantity = pending_campaign.target_quantity
    
    if pending_campaign.campaign_image != campaign.campaign_image:
        campaign.campaign_image = pending_campaign.campaign_image
        
    if campaign.status == Campaign.Status.APPROVED and pending_campaign.start_date != campaign.start_date:
        campaign.start_date = pending_campaign.start_date
        
    if campaign.status != Campaign.Status.APPROVED and pending_campaign.end_date != campaign.end_date:
        campaign.end_date = pending_campaign.end_date
        
    campaign.save()
    pending_campaign.status = PendingCampaign.Status.APPROVED
    pending_campaign.save()
    
    messages.success(request, f"Changes for campaign '{campaign.title}' have been approved.")
    return redirect("/dashboard/admin/?section=campaign-changes/")

@login_required
def reject_campaign_changes(request, campaign_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("campaigns")

    pending_campaign = PendingCampaign.objects.get(id=campaign_id)
    pending_campaign.status = PendingCampaign.Status.REJECTED
    pending_campaign.save()
    messages.info(request, f"Changes for campaign '{pending_campaign.campaign.title}' have been rejected.")
    return redirect("/dashboard/admin/?section=campaign-changes/")

@login_required
def delete_campaign_view(request, campaign_id):
    if request.user.role == 'DONOR':
        messages.error(request, "You do not have permission to delete a campaign.")
        return redirect("campaigns")
    
    campaign = Campaign.objects.get(id=campaign_id)
    
    if campaign.status == Campaign.Status.APPROVED and campaign.ngo.user != request.user:
        messages.error(request, "You do not have permission to delete this campaign.")
        return redirect("campaigns")
    
    campaign.delete()
    messages.success(request, "Campaign deleted successfully.")
    return redirect("campaigns")