from django.shortcuts import render


# Create your views here.

def index_view(request):
    """renders the front page"""
    return render(request, "core/index.html")


def post_view(request):
    """renders the post's detailed page"""
    return render(request, "core/post_detail.html")


def games_view(request):
    """renders the game page"""
    return render(request, "core/games.html")
