from django.shortcuts import render

def register_view(request):
    return render(request,"auth/register_page.html")

def login_view(request):
    return render(request,"auth/login_page.html")