from django.shortcuts import render, redirect

def campaign_view(request):
    return render(request,"main/campaign_page.html")