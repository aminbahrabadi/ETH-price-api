class BasePriceProvider:
    PRICE_URL = None
    PROVIDER_NAME = None
    PROVIDERS_MAP = {
        'UniSwapV3': 'apps.price_fetch.providers.gecko_terminal.UniSwapV3Provider',
    }

    @classmethod
    def _get_provider_cls(cls, provider_name: str):
        return cls.PROVIDERS_MAP.get(provider_name)

    @classmethod
    def get_provider_by_name(cls, provider_name):
        provider_class = cls._get_provider_cls(provider_name)
        if not provider_class:
            raise ValueError('Provider does not exist')
        return provider_class()
