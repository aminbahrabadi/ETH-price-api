from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, Q, Sum
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.base.rate_limits import GeneralThrottle
from apps.price_fetch.models import Price
from apps.price_fetch.providers.coin_gecko import CoinGeckoProvider
from apps.price_fetch.providers.uni_swap_v3 import UniSwapV3Provider


class GetPricesApiView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [GeneralThrottle]

    def _get_prices(self, days):
        CoinGeckoProvider.get_prices(number_of_days=days)
        UniSwapV3Provider.get_prices(number_of_days=days)

    def get(self, request):
        # get the prices
        self._get_prices(days=settings.DEFAULT_PRICE_DAYS)

        start_date_timestamp = Price.get_price_start_timestamp(days=settings.DEFAULT_PRICE_DAYS)
        providers = Price.objects.values_list('provider', flat=True).distinct()
        prices = (
            Price.objects.filter(timestamp__gte=start_date_timestamp)
            .values('symbol', 'timestamp')
            .annotate(
                **{
                    f'{provider}': ExpressionWrapper(
                        Coalesce(Sum('price', filter=Q(provider=provider)), 0),
                        output_field=DecimalField(max_digits=20, decimal_places=10),
                    )
                    for index, provider in enumerate(providers, start=1)
                }
            )
            .order_by('timestamp')
        )
        return Response(prices, status=status.HTTP_200_OK)
