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

from dotenv import load_dotenv
import os

load_dotenv()

rPassword = os.getenv("redisPassword")

r = redis.Redis(
    host="redis-16708.c11.us-east-1-3.ec2.cloud.redislabs.com",
    port=16708,
    password=rPassword,
)


def homePage(request):
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
    return render(
        request,
        "auction/homepage.html",
        {"list1": auctionItem.objects.filter(active=True)},
    )


def auctionClosed(request):
    return render(
        request,
        "auction/closeauction.html",
        {"list1": auctionItem.objects.filter(active=False)},
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
            item.endDate = item.startDate + timedelta(minutes=5)
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
            return listIndexAuction(request, listId)
        else:
            placeBid(listId, request.user.username, bidAmount)
            print("Si può inserire la puntata d'asta")
            messages.success(request, "Offerta correttamente inserita")
            return listIndexAuction(request, listId)
    else:
        print("Offerta troppo bassa")
        messages.error(
            request,
            "Offerta troppo bassa",
        )
        return listIndexAuction(request, listId)


def placeBid(auctionId, bidder, bidAmount):
    r.zadd(f"auction:{auctionId}", {bidder: bidAmount})


def getHighBid(listId):
    keyExists = r.zrange(f"auction:{listId}", 0, -1, withscores=True)
    if len(keyExists) > 0:
        highestBid = r.zrevrange(f"auction:{listId}", 0, 0, withscores=True)
        lastAmount = float(highestBid[0][1])
    else:
        auction = auctionItem.objects.get(id=listId)
        lastAmount = auction.startingBid
    return lastAmount


def getUserHighBid(listId):
    highestBid = r.zrevrange(f"auction:{listId}", 0, 0, withscores=True)
    if highestBid:
        userHighBid = highestBid[0][0]
    else:
        userHighBid = "Be the first bidder"
    return userHighBid


def sendTransaction(message):
    w3 = Web3(
        Web3.HTTPProvider(
            "https://goerli.infura.io/v3/ecadd76dd30247b4bf4fd9238723bba2"
        )
    )
    address = "0x3eDb1E13ae5D632a555128E57052B7662106DEa6"
    privateKey = os.getenv("privateKey")
    nonce = w3.eth.get_transaction_count(address, "pending")
    # w3.eth.get_transaction_count(address)
    gasPrice = w3.eth.gas_price
    value = w3.to_wei(0, "ether")
    signedTx = w3.eth.account.sign_transaction(
        dict(
            nonce=nonce,
            gasPrice=gasPrice,
            gas=100000,
            to="0x0000000000000000000000000000000000000000",
            value=value,
            data=message.encode("utf-8"),
        ),
        privateKey,
    )

    tx = w3.eth.send_raw_transaction(signedTx.rawTransaction)
    txId = w3.to_hex(tx)
    return txId


def auctionWin(request):
    return render(
        request,
        "auction/myprofile.html",
        {
            "list1": auctionItem.objects.filter(
                active=False, winner=request.user.username
            )
        },
    )
