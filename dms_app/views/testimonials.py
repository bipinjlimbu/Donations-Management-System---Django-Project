from django.shortcuts import render

def testimonials_view(request):
    return render(request, "main/testimonials_page.html")