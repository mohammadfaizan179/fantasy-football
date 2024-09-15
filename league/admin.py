from django.contrib import admin

from league.models import Team, Player, Transaction


# Register your models here.
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'capital']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'position', 'value', 'team', 'for_sale', 'sale_price']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'player', 'seller_team', 'buyer_team', 'transfer_amount', 'inactive']




