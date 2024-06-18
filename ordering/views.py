from django.shortcuts import render
from common.views import (
    BaseDetailView,
    BaseListView,
    ImageBaseListView,
    ImageBaseDetailView,
)
from ordering.models import Order, OrderItem, Shipping
from ordering.serializers import (
    OrderSerializer,
    ReadOrderSerializer,
    ShippingSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from products.models import Product
from django.core.mail import EmailMultiAlternatives
from rest_framework.parsers import FileUploadParser, MultiPartParser
import json
from thecart_auth.models import User


class OrderListView(ImageBaseListView):
    """
    """

    model = Order
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    read_serializer_class = ReadOrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date is not None and end_date is not None:
            self.filter_object = Q(created_at__range=(start_date, end_date))
        queryset = self.model.objects.filter(self.filter_object)
        return queryset

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


class OrderDetailView(ImageBaseDetailView):
    """
    """

    permission_classes = [IsAuthenticated]
    model = Order
    serializer_class = OrderSerializer
    read_serializer_class = ReadOrderSerializer


class ShippingListView(BaseListView):
    """
    """

    permission_classes = [IsAuthenticated]
    model = Shipping
    serializer_class = ShippingSerializer
    read_serializer_class = ShippingSerializer

    def get_queryset(self):
        if self.request.user.is_regular_user:
            self.filter_object = Q(user=self.request.user, is_deleted=False)
        else:
            self.filter_object = Q(is_deleted=False)
        queryset = self.model.objects.filter(self.filter_object)
        return queryset

    def get(self, request):
        all_status = request.GET.get("all", None)
        if all_status is not None:
            queryset = self.get_queryset(request)
            serializer = self.get_read_serializer_class()(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = self.get_queryset(request)
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


@api_view(["POST"])
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