from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class auctionItemForm(forms.ModelForm):
    class Meta:
        model = auctionItem
        fields = ("title", "description", "startingBid", "image_url")
