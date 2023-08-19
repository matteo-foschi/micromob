from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import *
from .forms import CustomUserCreationForm


def homePage(request):
    return render(request, "auction/homepage.html")
    # {"a1": auctionlist.objects.filter(active_bool=True), "a2": bids.objects},
    # )


def logIn(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("homePage"))
        else:
            return render(
                request,
                "auction/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auction/login.html")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in.
            login(request, user)
            return redirect("homePage")  # Redirect to a success page
    else:
        form = CustomUserCreationForm()
    return render(request, "auction/register.html", {"form": form})
