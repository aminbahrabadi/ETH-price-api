import datetime

import requests
from rest_framework import status

from apps.price_fetch.models import Price
from apps.price_fetch.providers.base import BasePriceProvider


class UniSwapV3Provider(BasePriceProvider):
    PROVIDER_NAME = 'UniSwapV3'
    API_ENDPOINT_URL = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'
    WETH_DEFAULT_POOL = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'

    @classmethod
    def get_prices(cls, pool_id=WETH_DEFAULT_POOL, number_of_days=30, symbol='WETH'):
        today = datetime.datetime.now()
        latest_price = Price.objects.filter(provider=cls.PROVIDER_NAME, symbol=symbol).order_by('-timestamp').first()
        num_days = number_of_days
        days_since_latest = (today - Price.get_date(latest_price.timestamp)).days if latest_price else number_of_days

        if days_since_latest > 0:
            days_missing = min(num_days, days_since_latest)
            start_date = (
                Price.get_date(latest_price.timestamp) + datetime.timedelta(days=1)
                if latest_price
                else today - datetime.timedelta(days=days_missing)
            )

            query = """
            {
              pools(where: {id: "%s"}) {
              token1 {
                 symbol
              }
                poolDayData(first: %d, orderBy: date, orderDirection: desc) {
                  pool {
                    id
                  }
                  token0Price
                  date
                }
              }
            }
            """ % (
                pool_id,
                days_missing,
            )
            request_data = {'query': query}

            try:
                response = requests.post(cls.API_ENDPOINT_URL, json=request_data)

                if response.status_code != status.HTTP_200_OK:
                    error_message = f'Error fetching data from GraphQL endpoint: {response.status_code}'
                    return {'error': error_message}

                data = response.json()
                symbol = data['data']['pools'][0]['token1']['symbol']
                price_objects = data['data']['pools'][0]['poolDayData']

                for price_object in price_objects:
                    if start_date.date() <= Price.get_date(price_object['date']).date():
                        Price.create_or_update(
                            provider=cls.PROVIDER_NAME,
                            price=price_object.get('token0Price', 0),
                            timestamp=Price.get_date(price_object.get('date', 0)).timestamp(),
                            pool=price_object.get('pool', {}).get('id'),
                            symbol=symbol,
                        )
                return True, {'result': 'success'}

            except Exception as e:
                error_message = f'An error occurred: {str(e)}'
                return False, {'result': error_message}

        else:
            return True, {'result': 'no data'}
