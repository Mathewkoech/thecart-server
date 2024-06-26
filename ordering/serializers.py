from .models import Order, OrderItem
from common.validators import non_zero_quantity
from rest_framework import serializers
# The OrderSerializer class is a subclass of serializers.ModelSerializer.
from ordering.models import Order, OrderItem, Shipping, Cart, CartItem
from common.serializers import BaseModelSerializer
from rest_framework import serializers
from common.validators import non_zero_quantity
from products.models import Product
from django.db import transaction
from products.serializers import ProductSerializer, ReadProductSerializer
from thecart_auth.serializers import UserSerializer


# ordering serializers
class ReadOrderItemSerializer(BaseModelSerializer):
    product = ReadProductSerializer(required=True)

    class Meta(BaseModelSerializer.Meta):
        model = OrderItem

class ReadOrderSerializer(BaseModelSerializer):
    value = serializers.SerializerMethodField()
    order_items = ReadOrderItemSerializer(many=True, read_only=True)

    def get_value(self, obj):
        return sum(item.value for item in obj.order_items.all())

    class Meta(BaseModelSerializer.Meta):
        model = Order

class OrderItemSerializer(BaseModelSerializer):
    quantity = serializers.IntegerField(validators=[non_zero_quantity])
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = OrderItem
        exclude = []


class OrderSerializer(BaseModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    order_items = OrderItemSerializer(many=True, required=True)

    class Meta(BaseModelSerializer.Meta):
        model = Order

    def create(self, validated_data):
        items_data = validated_data.pop("order_items")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, order, validated_data):
        items_data = validated_data.pop("order_items")
        with transaction.atomic():
            OrderItem.objects.filter(order=order).delete()
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        return order


class ShippingSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Shipping


class CartSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Cart


class CartItemSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = CartItem


class ReadCartItemSerializer(BaseModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = CartItem
