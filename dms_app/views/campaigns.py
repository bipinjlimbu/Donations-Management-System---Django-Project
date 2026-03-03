from datetime import date
from django.shortcuts import render, redirect
from ..models import Campaign
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

def campaigns_page_view(request):
    campaigns = Campaign.objects.exclude(status__in=[Campaign.Status.REJECTED, Campaign.Status.PENDING]).order_by('-approved_at')
    for campaign in campaigns:
        campaign.is_active = Campaign.is_active(campaign)
        campaign.is_completed = Campaign.is_completed(campaign)
        
    return render(request,"main/campaigns_page.html", {"campaigns": campaigns})

@user_passes_test(lambda u: u.role == 'NGO' or u.role == 'ADMIN')
def create_campaign_view(request):
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

@user_passes_test(lambda u: u.role == 'ADMIN' or u.role == 'NGO')
def approve_campaign_request(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    campaign.status = Campaign.Status.APPROVED
    campaign.approved_at = date.today()
    campaign.save()
    messages.success(request, f"Campaign '{campaign.title}' has been approved.")
    return redirect("admin-dashboard")

@user_passes_test(lambda u: u.role == 'ADMIN' or u.role == 'NGO')
def reject_campaign_request(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    campaign.status = Campaign.Status.REJECTED
    campaign.save()
    messages.info(request, f"Campaign '{campaign.title}' has been rejected.")
    return redirect("admin-dashboard")

def single_campaign_page_view(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    
    if campaign.status in [Campaign.Status.PENDING, Campaign.Status.REJECTED]:
        messages.warning(request, "This campaign is not available for viewing.")
        return redirect("campaigns")
    
    campaign.is_active = Campaign.is_active(campaign)
    campaign.is_completed = Campaign.is_completed(campaign)
    return render(request,"main/single_campaign_page.html", {"campaign": campaign})

def edit_campaign_view(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    campaign.is_active = Campaign.is_active(campaign)
    campaign.is_completed = Campaign.is_completed(campaign)
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
            elif end_date < start_date:
                errors["end_date"] = "End date must be after the start date."
        
        if errors:
            return render(request, "main/edit_campaign_page.html", {"errors": errors,"data": request.POST, "campaign": campaign})
        
        campaign.title = title
        campaign.description = description
        if campaign_image:
            campaign.campaign_image = campaign_image
        campaign.category = category
        campaign.item_type = item_type
        campaign.unit = unit
        campaign.target_quantity = target_quantity
        if campaign.status == Campaign.Status.APPROVED:
            campaign.start_date = start_date
        else:
            campaign.end_date = end_date
        campaign.save()
        
        messages.success(request, "Campaign updated successfully.")
        return redirect("campaigns")
    
    return render(request,"main/edit_campaign_page.html", {"campaign": campaign})