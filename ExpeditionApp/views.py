from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Expedition


def home(request):
    return HttpResponse("<h1>Welcome to TransConnect</h1>")


def welcome(request, name):
    return HttpResponse(f"Hello {name}")


def liste_expeditions(request):
    return render(request, 'expedition/list.html', {'liste': Expedition.objects.all()})


def detailsExpedition(request, pk):
    expedition = get_object_or_404(Expedition, pk=pk)
    return render(request, 'expedition/details.html', {'expedition': expedition})


def deleteExpedition(request, pk):
    expedition = get_object_or_404(Expedition, pk=pk)
    # suppression seulement après confirmation (POST), jamais avec un simple lien
    if request.method == 'POST':
        expedition.delete()
        return redirect('list')
    return render(request, 'expedition/delete.html', {'expedition': expedition})