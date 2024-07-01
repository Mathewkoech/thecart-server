from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


def non_zero_quantity(value):
    if value <= 0:
        raise serializers.ValidationError(_("Quantity must be greater than 0"))