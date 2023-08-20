from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class User(User):
    pass


class auctionItem(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    description = models.TextField()
    startingBid = models.IntegerField()
    image = models.ImageField(blank=True, null=True, upload_to="images/")
    active = models.BooleanField(default=True)
    startDate = models.DateTimeField(default=timezone.now)
    endDate = models.DateTimeField()
    winner = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Auction_Item, self).save(*args, **kwargs)
