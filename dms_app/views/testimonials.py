from django.shortcuts import render

def testimonials_view(request):
    return render(request, "main/testimonials_page.html")

def create_testimonial_view(request):
    return render(request, "main/create_testimonial_page.html")