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
    image_url = image_url = models.CharField(
        max_length=228, default=None, blank=True, null=True
    )
    active = models.BooleanField(default=True)
    startDate = models.DateTimeField(default=timezone.now)
    endDate = models.DateTimeField(default=timezone.now)
    winner = models.CharField(max_length=20, blank=True, null=True)
    txId = models.CharField(max_length=66, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(auctionItem, self).save(*args, **kwargs)


class auctionBid(models.Model):
    auction = models.ForeignKey(auctionItem, on_delete=models.CASCADE, default=1)
    bidderUser = models.CharField(max_length=100, null=True)
    bidAmount = models.FloatField()

    def save(self, *args, **kwargs):
        super(auctionBid, self).save(*args, **kwargs)
