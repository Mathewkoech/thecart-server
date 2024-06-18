from django.shortcuts import render
from django.http import JsonResponse
from .serializers import UserSerializer, 
CategorySerializer, 
ProductSerializer, 
OrderSerializer, 
OrderItemSerializer, 
CartSerializer, 
CartItemSerializer, 
AddressSerializer
from .models import User, Category, Product, Order, OrderItem, Cart, CartItem, Address

def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_product(request, pk):
    product = Product.objects.get(pk=pk)
    serializer = ProductSerializer(product)
    return JsonResponse(serializer.data, safe=False)

def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_category(request, pk):
    category = Category.objects.get(pk=pk)
    serializer = CategorySerializer(category)
    return JsonResponse(serializer.data, safe=False)

def get_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_order(request, pk):
    order = Order.objects.get(pk=pk)
    serializer = OrderSerializer(order)
    return JsonResponse(serializer.data, safe=False)

def get_order_items(request, pk):
    order_items = OrderItem.objects.filter(order=pk)
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_carts(request):
    carts = Cart.objects.all()
    serializer = CartSerializer(carts, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_cart(request, pk):
    """Retrieve a cart."""
    cart = Cart.objects.get(pk=pk)
    serializer = CartSerializer(cart)
    return JsonResponse(serializer.data, safe=False)

def get_cart_items(request, pk):
    """Retrieve all cart items in a cart."""
    cart_items = CartItem.objects.filter(cart=pk)
    serializer = CartItemSerializer(cart_items, many=True)
    return JsonResponse(serializer.data, safe=False)