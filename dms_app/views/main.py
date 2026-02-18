from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from ..models import Register

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