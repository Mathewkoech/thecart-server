from django.shortcuts import render
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

class OrderCreateView(APIView):
    """
    Create an order
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not serializer.validated_data['items']:  # Check if items list is empty
                return Response({"error": "Order must have at least one item"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(created_by=user, user=user, first_name=user.first_name, last_name=user.last_name, email=email)  # Set user based on authenticated user
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class OrderListView(ImageBaseListView):
    """
    Getting all orders
    """

    model = Order
    serializer_class = OrderSerializer
    # permission_classes = [AllowAny]
    read_serializer_class = ReadOrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date is not None and end_date is not None:
            self.filter_object = Q(created_at__range=(start_date, end_date))
        queryset = self.model.objects.filter(self.filter_object)
        return queryset

    @permission_classes([IsAuthenticated])
    def delete(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class OrderDetailView(ImageBaseDetailView):
    """
    Getting a single order
    """

    # permission_classes = [IsAuthenticated]
    model = Order
    serializer_class = OrderSerializer
    read_serializer_class = ReadOrderSerializer



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
        return CartItem.objects.filter(cart__user=self.request.user)

    def post(self, request):
        # Get product ID from request data
        product_id = request.data.get('product_id')

        # Validate data
        if not product_id:
            return Response({'error': 'Missing product ID'}, status=HTTP_400_BAD_REQUEST)

        product = Product.objects.get(pk=product_id)

        # Get user (if available)
        user = request.user  # This will be the authenticated user if logged in

        # Create a session key if it doesn't exist
        request.session.set_expiry(0)  # Set session cookie expiry to browser session

        # Retrieve cart items from session (or create an empty list)
        cart_items = request.session.get('cart', [])

        # Check if item already exists in cart (based on product ID)
        existing_item = next((item for item in cart_items if item['product_id'] == product_id), None)

        if existing_item:
            existing_item['quantity'] += 1
        else:
            cart_items.append({
                'product_id': product_id,
                'quantity': 1,
            })

        # Update session with cart items
        request.session['cart'] = cart_items

        return Response({'message': 'Item added to cart successfully'}, status=HTTP_200_OK)

    def remove_cart_item(self, request, product_id):
        """
        Remove cart item based on user and product ID.
        """
        if request.user.is_authenticated:
            # Remove item from database for authenticated users
            CartItem.objects.filter(user=request.user, product_id=product_id).delete()
        else:
            # Remove item from session cart list for anonymous users
            cart_items = request.session.get('cart', [])
            updated_cart = [item for item in cart_items if item['product_id'] != product_id]
            request.session['cart'] = updated_cart



class CartItemDetailView(BaseDetailView):
    model = CartItem
    serializer_class = CartItemSerializer
    read_serializer_class = ReadCartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(CartItem, id=self.kwargs['pk'], cart__user=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Only allow the user to delete their own cart items
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)