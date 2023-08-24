from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import *
from .forms import CustomUserCreationForm, auctionItemForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

from django.conf import settings
import json

import redis

r = redis.Redis(host="127.0.0.1", port=6379, password="", db=0, decode_responses=True)


def homePage(request):
    return render(
        request,
        "auction/homepage.html",
        {"list1": auctionItem.objects.filter(active=True)},
    )


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


def logOut(request):
    logout(request)
    return redirect("homePage")


def create(request):
    if request.method == "POST":
        form = auctionItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user.username
            item.endDate = item.startDate + timedelta(minutes=30)
            item.save()
            return redirect("homePage")  # Redirect to a success page
    else:
        form = auctionItemForm()
    return render(request, "auction/create.html", {"form": form})


def listIndexAuction(request, indexId):
    indexAuction = auctionItem.objects.get(id=indexId, active=True)
    lastBid = getHighBid(indexId)
    lastUserBid = getUserHighBid(indexId)
    return render(
        request,
        "auction/listauction.html",
        {"list": indexAuction, "lastBid": lastBid, "lastUserBid": lastUserBid},
    )


def bidList(request):
    bidAmount = float(request.GET["bidAmount"])
    listId = str(request.GET["listId"])
    itemAuction = auctionItem.objects.get(id=listId)
    lastBid = getHighBid(listId)
    lastUserBid = getUserHighBid(listId)
    if bidAmount > lastBid and bidAmount > itemAuction.startingBid:
        if lastUserBid == request.user.username:
            messages.error(
                request,
                "Your last bid is the best. You are the best bidder in the auction.",
            )
            return render(request, "auction/listauction.html", {"list": listId})
        else:
            placeBid(listId, request.user.username, bidAmount)
            print("Si può inserire la puntata d'asta")
    else:
        print("Offerta troppo bassa")
        messages.error(
            request,
            "Offerta troppo bassa",
        )
        return render(request, "auction/listauction.html", {"list": listId})

    indexAuction = auctionItem.objects.get(id=listId, active=True)
    return render(request, "auction/listauction.html", {"list": indexAuction})


def placeBid(auctionId, bidder, bidAmount):
    r.zadd(f"auction:{auctionId}", {bidder: bidAmount})
    all_bids = r.zrange(f"auction:{auctionId}", 0, -1, withscores=True)
    print(all_bids)


def getHighBid(listId):
    keyExists = r.zrange(f"auction:{listId}", 0, -1, withscores=True)
    if len(keyExists) > 0:
        highest_bid = r.zrevrange(f"auction:{listId}", 0, 0, withscores=True)
        lastAmount = float(highest_bid[0][1])
    else:
        lastAmount = 0
    return lastAmount


def getUserHighBid(listId):
    highest_bid = r.zrevrange(f"auction:{listId}", 0, 0, withscores=True)
    userHighBid = highest_bid[0][0]
    return userHighBid
