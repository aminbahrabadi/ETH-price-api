import requests
from django.conf import settings
from django.db.models import DecimalField, ExpressionWrapper, Q, Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views import View
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
            .order_by('-timestamp')[:30]
        )
        return Response(prices, status=status.HTTP_200_OK)


class AddressBalanceFetchView(View):
    def get(self, request, *args, **kwargs):
        address = kwargs.get('address')
        url = f'{settings.ARB_NETWORK_URL}/{settings.ALCHEMY_API_KEY}'
        payload = {
            'jsonrpc': '2.0',
            'method': 'alchemy_getTokenBalances',
            'params': [
                address,
                'erc20',
                {'maxCount': 100},
            ],
            'id': 0,
        }

        headers = {
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get('error'):
                return JsonResponse({'error': data['error']}, status=500)

            balances = data.get('result', {}).get('tokenBalances', [])
            arb_balances = []
            for balance in balances:
                arb_balances.append(
                    {
                        'contractAddress': balance['contractAddress'],
                        'tokenBalance': int(balance['tokenBalance'], 16) / 10e17,
                    }
                )

            return JsonResponse({'address': address, 'arb_balances': arb_balances})

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Request Error: {str(e)}'}, status=500)
