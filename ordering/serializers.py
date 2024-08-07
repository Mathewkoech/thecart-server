from .models import Order, OrderItem
from common.validators import non_zero_quantity
from rest_framework import serializers
# The OrderSerializer class is a subclass of serializers.ModelSerializer.
from ordering.models import Order, OrderItem, Shipping, CartItem
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
        exclude = []

class ReadOrderSerializer(BaseModelSerializer):
    order_items = ReadOrderItemSerializer(many=True, read_only=True)
    value = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price','shipping_address', 'order_items', 'value']

    def get_value(self, obj):
        return sum(item.value for item in obj.order_items.all())

    def to_representation(self, instance):
        """
        Override to_representation to conditionally include user information.
        """
        data = super().to_representation(instance)
        if not self.context['request'].user.is_authenticated:
            data.pop('user', None)  
            data['shipping_address'] = 'Address hidden'
        return data

class OrderItemSerializer(BaseModelSerializer):
    quantity = serializers.IntegerField(validators=[non_zero_quantity])
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = OrderItem
        exclude = []


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_method', 'contact_email', 'contact_phone']
        extra_kwargs = {
            'payment_method': {'required': True},
            'contact_email': {'required': True},
            'contact_phone': {'required': True},
        }



class OrderSerializer(BaseModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    order_items = OrderItemSerializer(many=True, required=True)

    class Meta(BaseModelSerializer.Meta):
        model = Order

    def validate_status(self, attrs):
        if attrs != Order.PENDING:
            raise serializers.ValidationError("Order status must be 'Pending' during creation.")
        return attrs

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


class CartItemSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = CartItem
        exclude = ()


class ReadCartItemSerializer(BaseModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = CartItem
        exclude = ()
        
    def get_product(self, obj):
        product_obj = obj.product
        if product_obj:
            product_serializer = ProductSerializer(product_obj)
            return {
                'id': product_obj.id,
                'name': product_serializer.data.get('name', ''),
                'brand': product_serializer.data.get('brand', ''),
                'description': product_serializer.data.get('description', ''),
                'image': product_serializer.data.get('image', ''),
            }
        return None
