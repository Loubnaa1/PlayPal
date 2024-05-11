from django.shortcuts import render

# Create your views here.


def landing(request):
    """A landing page view"""
    return render(request, 'landing/landing.html')
