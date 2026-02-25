from django.shortcuts import render, redirect

def campaigns_page_view(request):
    return render(request,"main/campaigns_page.html")

def create_campaign_view(request):
    return render(request,"main/create_campaign_page.html")