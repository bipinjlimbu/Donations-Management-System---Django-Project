from django.shortcuts import render, redirect
from ..models import Register, User
import re

def register_view(request):
    errors = {}
    if request.method == "POST":
        image = request.FILES.get("profile_image")
        username = request.POST.get("username").strip()
        name = request.POST.get("name").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirm_password").strip()
        role = request.POST.get("role")
        phone = request.POST.get("phone").strip()
        address = request.POST.get("address").strip()
        registration_number = request.POST.get("registration_number").strip()
        citizenship_number = request.POST.get("citizenship_number").strip()
        verification_document = request.FILES.get("verification_document")
        
        username_pattern = r'^[A-Z]{1}[a-z]{4,}[0-9]{2,}$'
        if not username:
            errors["username"] = "Username is required."
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Username already exists."
        elif not re.match(username_pattern, username):
            errors["username"] = "Username must start with an uppercase letter, followed by at least 4 lowercase letters, and end with at least 2 digits."
            
        if not name:
            errors["name"] = "Name is required."
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            errors["email"] = "Email is required."
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Email already exists."
        elif not re.match(email_pattern, email):
            errors["email"] = "Invalid email format."
        
        password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not password:
            errors["password"] = "Password is required."
        elif not re.match(password_pattern, password):
            errors["password"] = "Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character."
        elif password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."
            
        phone_pattern = r'^[0-9]{9,15}$'
        if not phone:
            errors["phone"] = "Phone number is required."
        elif not re.match(phone_pattern, phone):
            errors["phone"] = "Invalid phone number format."
            
        if not address:
            errors["address"] = "Address is required."
            
        if role == "NGO" and not registration_number:
            errors["registration_number"] = "Registration number is required for NGOs."
            
        if role == "Donor" and not citizenship_number:
            errors["citizenship_number"] = "Citizenship number is required for Donors."
            
        if not verification_document:
            errors["verification_document"] = "Verification document is required."
        
        if errors:
            return render(request, "auth/register_page.html", {"errors": errors})
        else:
            Register.objects.create(
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