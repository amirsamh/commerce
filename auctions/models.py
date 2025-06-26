from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return self.category


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    img = models.CharField(max_length=500, null=True, blank=True)
    startbid = models.FloatField(max_length=64)
    category = models.CharField(max_length=64)
    creator = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    winner = models.CharField(max_length=64, null=True, blank=True) 

    def __str__(self):
        return self.title


class Comment(models.Model):
    writer = models.CharField(max_length=64)
    text = models.CharField(max_length=500)
    item = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.writer} on {self.item}"


class Watchlist(models.Model):
    creator = models.CharField(max_length=64)
    listing = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.creator}, {self.listing}"


class Bid(models.Model):
    user = models.CharField(max_length=64)
    amount = models.FloatField(max_length=64)
    item = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.amount} $ on {self.item} by {self.user}"