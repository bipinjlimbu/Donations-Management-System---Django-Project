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

@login_required
def mark_all_notifications_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("notifications")

@login_required
def toggle_notification_read_view(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    if notification:
        notification.is_read = not notification.is_read
        notification.save()
        messages.success(request, "Notification marked as read.")
    else:
        messages.error(request, "Notification not found.")
    return redirect("notifications")

@login_required
def delete_notification_view(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    if notification:
        notification.delete()
        messages.success(request, "Notification deleted successfully.")
    else:
        messages.error(request, "Notification not found.")
    return redirect("notifications")