from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class GeneralThrottle(AnonRateThrottle):
    rate = '10/minute'
