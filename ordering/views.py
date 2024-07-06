from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from common.views import (
    BaseDetailView,
    BaseListView,
    ImageBaseListView,
    ImageBaseDetailView,
)
from ordering.models import Order, OrderItem, Shipping, CartItem
from ordering.serializers import (
    OrderSerializer,
    ReadOrderSerializer,
    ShippingSerializer,
    CartItemSerializer,
    ReadCartItemSerializer,
    OrderUpdateSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from products.models import Product
from django.core.mail import EmailMultiAlternatives
from rest_framework.parsers import FileUploadParser, MultiPartParser
import json
from thecart_auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from decimal import Decimal

class OrderCreateView(APIView):
    # permission_classes = [AllowAny]

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Retrieve cart items from session or CartItem model based on user authentication
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart_items = request.session.get('cart', [])

        if not cart_items:
            return Response({'error': 'No items in the cart'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price and gather order items
        total_price = Decimal('0.00')
        order_items = []
        for item in cart_items:
            if request.user.is_authenticated:
                product = item.product
                quantity = item.quantity
            else:
                product = Product.objects.get(pk=item['product_id'])
                quantity = item['quantity']
            price = product.price
            total_price += price * quantity
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'value': price * quantity,
            })

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='pending',
        )

        # Create order items
        for item_data in order_items:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                value=item_data['value'],
            )

        # Clear the cart after order creation
        if request.user.is_authenticated:
            cart_items.delete()
        else:
            del request.session['cart']

        # Return response with order details
        return Response({"order_id": order.id, "total_amount": total_price}, status=status.HTTP_201_CREATED)


class OrderListView(ImageBaseListView):
    """
    Getting all orders
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = ReadOrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class OrderDetailView(ImageBaseDetailView):
    """
    Getting a single order
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReadOrderSerializer(order, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class CheckoutOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        """
        Retrieve all checkout orders for the authenticated user or a specific order if order_id is provided.
        """
        if order_id:
            order = Order.objects.get(pk=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            user_orders = Order.objects.filter(user=request.user)
            if not user_orders.exists():
                return Response({'error': 'No orders found for this user.'}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the orders
            serializer = OrderSerializer(user_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id, user=request.user, status="pending")
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or already checked out'}, status=status.HTTP_404_NOT_FOUND)
        user_orders = Order.objects.filter(user=request.user)
        if not user_orders.exists():
            return Response({'error': 'No orders found for checkout. Please create an order first.'}, status=HTTP_400_BAD_REQUEST)

        required_fields = ["address", "city", "state", "zip_code", "contact_email", "contact_phone"]
        for field in required_fields:
            if field not in request.data:
                return Response({f'error': f'{field} is required'}, status=HTTP_400_BAD_REQUEST)

        user = request.user
        shipping_address = Shipping(
            user=user,
            address=request.data["address"],
            city=request.data["city"],
            state=request.data["state"],
            zip_code=request.data["zip_code"]
            )
        shipping_address.save()  # Save the ShippingAddress object first (optional)

        order.shipping_address = shipping_address
        order.contact_email = request.data.get("contact_email", None)
        order.contact_phone = request.data.get("contact_phone", None)
        order.status = "completed"
        order.save()


        return Response({'message': 'Order checkout successful! Wait for delivery within 24 hours.'}, status=status.HTTP_200_OK)


class CheckoutOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all checkout orders for the authenticated user.
        """
        user_orders = Order.objects.filter(user=request.user)
        if not user_orders.exists():
            return Response({'error': 'No orders found for this user.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(user_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ShippingListView(BaseListView):
    """
    Getting all shipping
    """

    # permission_classes = [IsAuthenticated]
    model = Shipping
    serializer_class = ShippingSerializer
    read_serializer_class = ShippingSerializer

    def get_queryset(self):
        """
        
        """
        if self.request.user.is_authenticated and self.request.user.is_regular_user:
            self.filter_object = Q(user=self.request.user, is_deleted=False)
        else:
            self.filter_object = Q(is_deleted=False)
        queryset = self.model.objects.filter(self.filter_object)
        return queryset

    def get(self, request):
        all_status = request.GET.get("all", None)
        if all_status is not None:
            queryset = self.get_queryset()
            serializer = self.get_read_serializer_class()(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            serializer = self.get_read_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        """

        serializer = self.get_serializer_class()(
            data=request.data, context={"role": request.user.role}
        )
        if serializer.is_valid():
            user = request.user
            serializer.save(
                created_by=user, user=user,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShippingDetailView(BaseDetailView):
    """
    """

    permission_classes = [IsAuthenticated]
    model = Shipping
    serializer_class = ShippingSerializer
    read_serializer_class = ShippingSerializer

#order creation
@api_view(["POST"])
def postorder_url(request):
    parser_classes = [MultiPartParser]
    data = request.POST
    if data is not None:
        order = Order.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            address=data["address"],
            city=data["city"],
        )

        order_items = json.loads(data["order_items"])
        total = 0
        items = 0
        for order_item in order_items:
            product = Product.objects.get(pk=order_item["product"]["id"])
            OrderItem.objects.create(
                product=product, quantity=order_item["quantity"], order=order
            )
            total += product.price * order_item["quantity"]
            items = items + 1

        order.total = total
        order.items = items
        order.save()
        if request.user.is_authenticated:
            order.user = request.user
            order.save()
            return Response(status=status.HTTP_200_OK)


@api_view(["POST"])# completing an order
def complete_order(request):
    data = request.data
    if data is not None:
        order = Order.objects.get(pk=data["id"])
        order.status = "Shipped"
        user = User.objects.get(id=data["delivered_by"])
        order.delivered_by = user
        order.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def confirm_order(request):
    data = request.data
    if data is not None:
        order = Order.objects.get(pk=data["id"])
        order.order_status = "confirmed"
        order.save()
        return Response(status=status.HTTP_200_OK)


class CartItemListView(BaseListView):
    model = CartItem
    serializer_class = CartItemSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User can only see their own cart items
        return CartItem.objects.filter(user=self.request.user)
    def get(self, request):
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        cart_items = request.session.get('cart', [])
        if not cart_items:
            return Response([], status=status.HTTP_200_OK)
        
        serialized_cart_items = []
        for item in cart_items:
            product = Product.objects.get(pk=item['product_id'])
            serialized_cart_items.append({
                'product': product.name,
                'quantity': item['quantity'],
                'price': product.price
            })
        
        return Response(serialized_cart_items, status=status.HTTP_200_OK)

    def post(self, request):
        items = request.data

        if not isinstance(items, list):
            return Response({'error': 'Request body must be a list of items'}, status=status.HTTP_400_BAD_REQUEST)

        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)  # Default quantity to 1 if not provided by user

            if not product_id:
                return Response({'error': 'Missing product ID'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if user is authenticated
            if request.user.is_authenticated:
                # Add to cart using CartItem model
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user, product=product,
                    defaults={'quantity': quantity}
                )
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
            else:
                # Add to session-based cart
                cart_items = request.session.get('cart', [])
                existing_item = next((i for i in cart_items if i['product_id'] == product_id), None)
                if existing_item:
                    existing_item['quantity'] += quantity
                else:
                    cart_items.append({'product_id': product_id, 'quantity': quantity})
                request.session['cart'] = cart_items

        return Response({'message': 'Items added to cart successfully'}, status=status.HTTP_200_OK)

class RemoveCartItemView(View):
    def post(self, request, operation, product_id=None):
        """
        Remove cart item(s) based on user and operation.
        """
        if operation == 'single':
            if product_id:
                return self.remove_single_item(request, product_id)
            else:
                return JsonResponse({'error': 'Product ID is required for single item removal'}, status=400)
        elif operation == 'all':
            return self.remove_all_items(request)
        else:
            return JsonResponse({'error': 'Invalid operation'}, status=400)

    def remove_single_item(self, request, product_id):
        """
        Remove a single cart item based on user and product ID.
        """
        if request.user.is_authenticated:
            try:
                cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
                cart_item.delete()
                print(f"Item {product_id} removed from session carteeee")
                logger.info(f"Item with product_id {product_id} removed from cart for user {request.user.username}")
                return JsonResponse({'message': 'Item removed from cart successfully'}, status=200)
            except CartItem.DoesNotExist:
                return JsonResponse({'error': 'Cart item not found or already removed'}, status=404)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Handle cart removal for unauthenticated  users
            cart_items = request.session.get('cart', [])
            updated_cart = [item for item in cart_items if item['product_id'] != product_id]
            request.session['cart'] = updated_cart
            print(f"Item {product_id} removed from session cart")
            return JsonResponse({'message': 'Item removed from cart successfully'}, status=200)

    def remove_all_items(self, request):
        """
        Remove all cart items for the authenticated user.
        """
        if request.user.is_authenticated:
            try:
                CartItem.objects.filter(user=request.user).delete()
                return JsonResponse({'message': 'All items removed from cart successfully'}, status=200)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Handle cart removal for unauthenticated users
            request.session['cart'] = []
            return JsonResponse({'message': 'All items removed from cart successfully'}, status=200)
    



class CartItemDetailView(BaseDetailView):
    model = CartItem
    serializer_class = CartItemSerializer
    read_serializer_class = ReadCartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(CartItem, id=self.kwargs['pk'], cart__user=self.request.user)

    def get(self, request):
        if request.user.is_authenticated:
            # Fetch cart items for authenticated user
            cart_items = CartItem.objects.filter(user=request.user)
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Fetch cart items from session if not authenticated
            cart_items = request.session.get('cart', [])
            # Assuming cart_items is a list of dictionaries
            return Response(cart_items, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        # Only allow the user to delete their own cart items
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)