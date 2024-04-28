import datetime

import requests
from django.conf import settings

from apps.price_fetch.models import Price
from apps.price_fetch.providers.base import BasePriceProvider


class CoinGeckoProvider(BasePriceProvider):
    PROVIDER_NAME = 'CoinGecko'
    BASE_URL = 'https://api.coingecko.com/api/v3'
    COINS_MARKET_CHART_ENDPOINT = '/coins/{coin_id}/market_chart'
    WETH_ID = 'ethereum'

    @classmethod
    def get_prices(cls, symbol='WETH', number_of_days=settings.DEFAULT_PRICE_DAYS):
        today = datetime.datetime.now()
        latest_price = Price.objects.filter(provider=cls.PROVIDER_NAME, symbol=symbol).order_by('-timestamp').first()
        num_days = number_of_days
        days_since_latest = (today - Price.get_date(latest_price.timestamp)).days if latest_price else number_of_days

        if days_since_latest > 0:
            days_missing = min(num_days, days_since_latest)
            start_date = (
                (Price.get_date(latest_price.timestamp) + datetime.timedelta(days=1))
                if latest_price
                else today - datetime.timedelta(days=days_missing)
            )

            vs_currency = 'usd'
            interval = 'daily'
            days = days_missing

            url = cls.BASE_URL + cls.COINS_MARKET_CHART_ENDPOINT.format(coin_id=cls.WETH_ID)
            params = {
                'id': cls.WETH_ID,
                'vs_currency': vs_currency,
                'days': days,
                'x_cg_demo_api_key': settings.COINGECKO_API_KEY,
                'interval': interval,
            }

            try:
                response = requests.get(
                    url,
                    params=params,
                )
                response.raise_for_status()

                data = response.json()
                prices = [price[1] for price in data['prices']]

                for i, price_object in enumerate(prices):
                    if start_date.date() <= Price.get_date(data['prices'][i][0] // 1000).date():
                        Price.create_or_update(
                            provider=cls.PROVIDER_NAME,
                            price=data['prices'][i][1],
                            timestamp=(Price.get_date(data['prices'][i][0] // 1000)).timestamp(),
                            symbol=symbol,
                        )
                return True, {'result': 'success'}

            except requests.RequestException as e:
                error_message = f'Error fetching data from CoinGecko: {e}'
                return False, {'result': error_message}

        else:
            return True, {'result': 'no data'}
