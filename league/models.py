from django.conf import settings
from django.db import models


class Team(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slogan = models.CharField(max_length=255)
    capital = models.DecimalField(max_digits=10, decimal_places=2, default=5000000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_value(self):
        return sum(player.value for player in self.players.all())


class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('ATT', 'Attacker'),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=1000000.00)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    for_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    seller_team = models.ForeignKey(Team, related_name='sales', on_delete=models.CASCADE)
    buyer_team = models.ForeignKey(Team, related_name='purchases', on_delete=models.CASCADE, null=True, blank=True)
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    inactive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
