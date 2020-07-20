from importlib import import_module

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _


class OrderAdapter(object):
    def __init__(self, order):
        self.order = order

    def get_return_url(self, *args, success=None, **kwargs) -> str:
        """
        Method used to determine the final url the client should see after
        returning from gateway. Client will be redirected to this url after
        backend handled the original callback (i.e. updated payment status)
        and only if SUCCESS_URL or FAILURE_URL settings are NOT set.
        By default it returns the result of `get_absolute_url`
        """
        return self.get_absolute_url()

    def get_absolute_url(self):
        """
        Standard method recommended in Django docs. It should return
        the URL to see details of particular Order.
        """
        raise NotImplementedError

    def is_ready_for_payment(self):
        """Most of the validation is made in PaymentMethodForm using but if you
        need any extra validation. For example you most probably want to disable
        making another payment for order that is already paid."""

        if hasattr(self.order, "is_ready_for_payment"):
            return self.order.is_ready_for_payment()

        return True

    def get_items(self):
        """
        There are backends that require some sort of item list to be attached
        to the payment. But it's up to you if the list is real or contains only
        one item called "Payment for stuff in {myshop}" ;)
        :return: List of {"name": str, "quantity": Decimal, "unit_price": Decimal} dicts.
        """
        return [
            {
                "name": self.order.get_description(),
                "quantity": 1,
                "unit_price": self.order.get_total_amount(),
            }
        ]

    def get_total_amount(self):
        """
        This method must return the total value of the Order.
        :return: Decimal object
        """
        raise NotImplementedError

    def get_user_info(self):
        """
        This method should return dict with necessary user info.
        For most backends email should be sufficient.
        Expected field names: `email`, `first_name`, `last_name`, `phone`
        """
        raise NotImplementedError

    def get_description(self):
        """
        :return: Description of the Order. Should return the value of appropriate field.
        """
        raise NotImplementedError

    def get_currency(self, default='pln'):
        return getattr(self.order, "currency", None) or default



def get_order_adapter(order):
    return OrderAdapter(order)

    # =====================

    # if not getattr(settings, 'GETPAID_ORDER_ADAPTER', None):
    #     return order

    # OrderAdapter = import_string(app_settings.ADAPTER)
    # return OrderAdapter(order)
