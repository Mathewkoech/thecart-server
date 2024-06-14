from .models import Product, Order
from rest_framework import serializers

# The ProductSerializer and OrderSerializer classes are subclasses of serializers.ModelSerializer.
# The Meta class is used to define the model and fields that will be serialized.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

