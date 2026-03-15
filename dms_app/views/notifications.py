from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Notification

@login_required
def notifications_view(request):
    context = {}
    
    context["alert_notification"] = Notification.objects.filter(user=request.user, is_read=False).exists()
    context["notifications"] = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request,"main/notifications_page.html", context)

