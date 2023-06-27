from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse, reverse_lazy


class IndexMain(View):
    def get(self, request):
        return render(request, "index.html")
