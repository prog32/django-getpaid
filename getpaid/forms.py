from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

import swapper
from getpaid.validators import run_getpaid_validators

from .adapter import get_order_adapter

Order = swapper.load_model("getpaid", "Order")


class PaymentMethodForm(forms.ModelForm):
    """
    Usable example.
    Displays all available payments backends as choice list.
    """

    order = forms.ModelChoiceField(
        widget=forms.HiddenInput, queryset=Order.objects.all()
    )

    class Meta:
        model = swapper.load_model("getpaid", "Payment")
        fields = [
            "order",
            # "amount_required",
            # "description",
            # "currency",
            "backend"
        ]
        widgets = {
            "amount_required": forms.HiddenInput,
            "description": forms.HiddenInput,
            "currency": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        from .registry import registry

        super().__init__(*args, **kwargs)
        order = self.initial.get("order")
        order_adapter = get_order_adapter(order)

        currency = order_adapter.get_currency()

        backends = registry.get_choices(currency)
        params = dict(
            choices=backends,
            initial=backends[0][0] if len(backends) == 1 else "",
            label=_("Payment backend"),
            widget=forms.RadioSelect,
        )
        hide_lonely = getattr(settings, "GETPAID", {}).get("HIDE_LONELY_PLUGIN", False)
        if hide_lonely and len(backends) == 1:
            params["initial"] = backends[0][0]
            params["widget"] = forms.HiddenInput

        self.fields["backend"] = forms.ChoiceField(**params)

    def clean_order(self):
        order_adapter = get_order_adapter(self.cleaned_data["order"])
        if not order_adapter.is_ready_for_payment():
            raise forms.ValidationError(_("Order cannot be paid"))

        return self.cleaned_data["order"]

    def clean(self):
        self.cleaned_data = super().clean()

        order = self.initial.get("order")
        order_adapter = get_order_adapter(order)

        self.cleaned_data["amount_required"] = order_adapter.get_total_amount()
        self.cleaned_data["currency"] = 'pln'
        self.cleaned_data["description"] = order_adapter.get_description()
        return run_getpaid_validators(self.cleaned_data)
