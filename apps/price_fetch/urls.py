from django.urls import path

from . import views


urlpatterns = [
    path('get-eth-prices/', views.GetPricesApiView.as_view(), name='eth_prices'),
]
