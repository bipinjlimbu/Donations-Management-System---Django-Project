from django.shortcuts import render, redirect
from ..models import Register

def register_view(request):
    if request.method == "POST":
        image = request.FILES.get("profile_image")
        username = request.POST.get("username")
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        registration_number = request.POST.get("registration_number")
        citizenship_number = request.POST.get("citizenship_number")
        verification_document = request.FILES.get("verification_document")
        
        user = Register.objects.create(
            name=name,
            username=username,
            email=email,
            password=password,
            role=role,
            phone=phone,
            address=address,
            profile_image=image,
            registration_number=registration_number,
            citizenship_number=citizenship_number,
            verification_document=verification_document
        )
        
        return redirect("home")
         
    return render(request,"auth/register_page.html")

def login_view(request):
    return render(request,"auth/login_page.html")