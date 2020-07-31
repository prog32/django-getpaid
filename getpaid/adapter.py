from importlib import import_module

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _


class OrderAdapter(object):
    def __init__(self, order):
        self.order = order

    def __getattr__(self, attr):
        return getattr(self.order, attr)


def get_order_adapter(order):
    if getattr(settings, 'GETPAID_ORDER_ADAPTER', None):
        CustomOrderAdapter = import_string(settings.GETPAID_ORDER_ADAPTER)
        return CustomOrderAdapter(order)

    return OrderAdapter(order)
