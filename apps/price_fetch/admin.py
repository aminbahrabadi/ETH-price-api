from django.contrib import admin

from apps.price_fetch.models import Price


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('price', 'timestamp', 'provider')
