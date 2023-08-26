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

import hashlib

from django.conf import settings
import json

import redis

from web3 import Web3
from .utils import sendTransaction

from dotenv import load_dotenv

from django.http import HttpResponse, HttpResponseBadRequest

import os

load_dotenv()

# rPassword = os.getenv("redisPassword") Not possibile to use .gitignore in PythonanyWhere
rPassword = "m5hLKUYYHAYheZjoJvQ9at7tGUwFSXOo"

# Setup REDIS in Clous
r = redis.Redis(
    host="redis-16708.c11.us-east-1-3.ec2.cloud.redislabs.com",
    port=16708,
    password=rPassword,
    decode_responses=True,
)


# Home Page - List of all the auction available and that are not conluded
def homePage(request):
    if auctionItem.objects.filter(active=True).exists():
        auctions = auctionItem.objects.filter(active=True)
        for auction in auctions:
            if auction.endDate <= timezone.now():
                auction.active = False
                auction.bidWinner = getHighBid(auction.id)
                auction.winner = getUserHighBid(auction.id)
                data = {
                    "ID": auction.id,
                    "Auction tile": auction.title,
                    "Start Auction price": auction.startingBid,
                    "End Auction price": auction.bidWinner,
                    "Winner user": auction.winner,
                }
                jsonString = json.dumps(data)
                hash = hashlib.sha256(jsonString.encode("utf-8")).hexdigest()
                txId = sendTransaction(hash)
                auction.txId = txId
                auction.save()
    else:
        messages.error(
            request,
            "We are so sorry but there aren't auctions Active now.",
        )
    return render(
        request,
        "auction/homepage.html",
        {"list1": auctionItem.objects.filter(active=True)},
    )


# Auction Closed - List of all the auction that are conluded
def auctionClosed(request):
    if not auctionItem.objects.filter(active=False).exists():
        messages.error(
            request,
            "There aren't auctions closed yet.",
        )
    return render(
        request,
        "auction/closeauction.html",
        {"list1": auctionItem.objects.filter(active=False)},
    )


# Log in procedure
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


# Register procedure
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


# Log out procedure
def logOut(request):
    logout(request)
    return redirect("homePage")


# Create procedure limited to admin
def create(request):
    if request.method == "POST":
        form = auctionItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user.username
            item.endDate = item.startDate + timedelta(days=5)
            item.save()
            return redirect("homePage")  # Redirect to a success page
    else:
        form = auctionItemForm()
    return render(request, "auction/create.html", {"form": form})


# View in detail of one auction and possibility to bid the auction
def listIndexAuction(request, indexId):
    indexAuction = auctionItem.objects.get(id=indexId, active=True)
    lastBid = getHighBid(indexId)
    lastUserBid = getUserHighBid(indexId)
    return render(
        request,
        "auction/listauction.html",
        {"list": indexAuction, "lastBid": lastBid, "lastUserBid": lastUserBid},
    )


# Procedure to BID the autction - All the data store in REDIS
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
                "Bid NOT accepted. Your last bid is the best. You are the best bidder in the auction.",
            )
            return listIndexAuction(request, listId)
        else:
            placeBid(listId, request.user.username, bidAmount)
            messages.success(
                request, "Auction bid successfully entered. You are the highest bidder."
            )
            return listIndexAuction(request, listId)
    else:
        messages.error(
            request,
            "Bid NOT accepted. Your bid is lower than the current bid. Please enter a higher bid than the current price.",
        )
        return listIndexAuction(request, listId)


# Procedure to place the bid in REDIS
def placeBid(auctionId, bidder, bidAmount):
    r.zadd(f"auction:{auctionId}", {bidder: bidAmount})


# Procedure to get the best bid for "listId" auction
def getHighBid(listId):
    keyExists = r.zrange(f"auction:{listId}", 0, -1, withscores=True)
    if len(keyExists) > 0:
        highestBid = r.zrevrange(f"auction:{listId}", 0, 0, withscores=True)
        lastAmount = float(highestBid[0][1])
    else:
        auction = auctionItem.objects.get(id=listId)
        lastAmount = auction.startingBid
    return lastAmount


# Procedure to get the best bidder for "listId" auction
def getUserHighBid(listId):
    highestBid = r.zrevrange(f"auction:{listId}", 0, 0, withscores=True)
    if highestBid:
        userHighBid = highestBid[0][0]
    else:
        userHighBid = "Be the first bidder"
    return userHighBid


# List of all the bid closed and filtered for username
def auctionWin(request):
    if auctionItem.objects.filter(active=False, winner=request.user.username).exists():
        return render(
            request,
            "auction/myprofile.html",
            {
                "list1": auctionItem.objects.filter(
                    active=False, winner=request.user.username
                )
            },
        )
    else:
        messages.error(
            request,
            "We are so sorry but there aren't auctions closed that you won.",
        )
        return render(
            request,
            "auction/myprofile.html",
            {
                "list1": auctionItem.objects.filter(
                    active=False, winner=request.user.username
                )
            },
        )
