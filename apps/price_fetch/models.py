from datetime import datetime, timedelta

from django.db import models


class Price(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pool = models.CharField(max_length=255, null=True, blank=True)
    symbol = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=10)

    @classmethod
    def get_date(cls, timestamp):
        """
        Convert Unix timestamp to datetime object.
        """
        return datetime.utcfromtimestamp(timestamp).replace(hour=0, minute=0, second=0, microsecond=0)

    @classmethod
    def create_or_update(cls, provider, timestamp, price, symbol, pool=None):
        if cls.objects.filter(symbol=symbol, provider=provider, timestamp=timestamp).exists():
            return Price.objects.filter(symbol=symbol, provider=provider, timestamp=timestamp).update(price=price)

        return cls.objects.create(
            provider=provider,
            pool=pool,
            timestamp=timestamp,
            price=price,
            symbol=symbol,
        )

    @classmethod
    def get_price_start_datetime(cls, days):
        return (datetime.today() - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)

    @classmethod
    def get_price_start_timestamp(cls, days):
        return cls.get_price_start_datetime(days=days).timestamp()
