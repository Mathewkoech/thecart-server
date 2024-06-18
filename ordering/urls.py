from django.urls import path
from ordering.views import (
    OrderListView,
    OrderDetailView,
    ShippingListView,
    ShippingDetailView,
    postorder_url,
    complete_order,
    confirm_order
)
app_name = "ordering"
urlpatterns = [
    path("", OrderListView.as_view(), name="orders"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("post/", postorder_url, name="post_order"),
    path("shippings/", ShippingListView.as_view(), name="shipping"),
    path("shippings/<uuid:pk>/", ShippingDetailView.as_view(), name="shipping_detail"),
    path("completeorder/", complete_order, name="completeorder"),
    path("confirmorder/", confirm_order, name="confirmorder"),
]