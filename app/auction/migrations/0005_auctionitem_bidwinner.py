# Generated by Django 4.2.4 on 2023-08-24 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auction", "0004_auctionbid"),
    ]

    operations = [
        migrations.AddField(
            model_name="auctionitem",
            name="bidWinner",
            field=models.IntegerField(default=None, null=True),
        ),
    ]