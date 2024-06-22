from django.urls import path
from ordering.views import (
    OrderListView,
    OrderDetailView,
    ShippingListView,
    ShippingDetailView,
    postorder_url,
    complete_order,
    confirm_order,
    CartListView,
    CartDetailView,
    CartItemListView,
    CartItemDetailView
)
app_name = "ordering"
urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path("<uuid:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("post/", postorder_url, name="post_order"),
    path("shippings/", ShippingListView.as_view(), name="shipping"),
    path("shippings/<uuid:pk>/", ShippingDetailView.as_view(), name="shipping_detail"),
    path("completeorder/", complete_order, name="completeorder"),
    path("confirmorder/", confirm_order, name="confirmorder"), # confirmorder 
    path('cart/', CartListView.as_view(), name='cart-list'), # cart-list
    path('cart/<int:pk>/', CartDetailView.as_view(), name='cart-detail'), # cart-detail
    path('cart-item/', CartItemListView.as_view(), name='cartitem-list'), # cartitem-list
    path('cart-item/<int:pk>/', CartItemDetailView.as_view(), name='cartitem-detail'), # cartitem-detail
]