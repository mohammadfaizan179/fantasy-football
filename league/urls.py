from django.urls import path, include
from rest_framework.routers import DefaultRouter
from league.views import TeamViewSet, PlayerViewSet, SetPlayerForSaleAPIView, RemovePlayerFromSaleAPIView, \
    PlayersForSaleAPIView, BuyPlayerAPIView, TransactionsHistoryAPIView, TransactionHistoryAPIView, \
    MyTransactionsHistoryAPIView

router = DefaultRouter()
router.register("league/team", TeamViewSet, basename="team")
router.register("team/player", PlayerViewSet, basename="player")

urlpatterns = [
    path("", include(router.urls)),

    # Transfer Market Endpoints
    path("player/<int:pk>/set-for-sale/", SetPlayerForSaleAPIView.as_view(), name='set_player_for_sale'),
    path("player/<int:pk>/remove-from-sale/", RemovePlayerFromSaleAPIView.as_view(), name='remove_player_from_sale'),
    path("players/for/purchase/", PlayersForSaleAPIView.as_view(), name='players_for_sale'),
    path("player/<int:pk>/buy/", BuyPlayerAPIView.as_view(), name='buy_player'),

    # Transaction History Endpoints
    path("transactions/history/", TransactionsHistoryAPIView.as_view(), name='transactions_history/'),
    path("transaction/<int:pk>/history/", TransactionHistoryAPIView.as_view(), name='transaction_history'),
    path("my/transactions/", MyTransactionsHistoryAPIView.as_view(), name='my_transactions_history'),

]
