from django.shortcuts import render


def home(request):
    """ View to render home page """
    return render(request, 'index.html')
