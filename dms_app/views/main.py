from django.shortcuts import render

def home_view(request):
    return render(request,"main/home_page.html")

def admin_dashboard_view(request):
    return render(request,"main/admin_dashboard.html")