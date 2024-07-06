from django.urls import path
from ordering.views import (
    OrderListView,
    OrderDetailView,
    ShippingListView,
    ShippingDetailView,
    postorder_url,
    complete_order,
    confirm_order,
    CartItemListView,
    CartItemDetailView,
    OrderCreateView,
    CheckoutOrderListView,
    RemoveCartItemView,
    CheckoutOrderDetailView,
)
app_name = "ordering"
urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path('orders/create/', OrderCreateView.as_view(), name='create_order'),
    path('orders/checkout/', CheckoutOrderListView.as_view(), name='checkout_orders'),
    path('orders/checkout/<uuid:order_id>/', CheckoutOrderListView.as_view(), name='checkout_orders'),
    # path('orders/checkout/<order_id>/', CheckoutOrderView.as_view(), name='checkout_order'),
    # path('orders/checkout/<uuid:order_id>/', CheckoutOrderView.as_view(), name='checkout_order_detail'),
    path("orders/<uuid:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("<int:pk>/delete/", OrderDetailView.as_view(), name="order-delete"),
    path('cart/remove/<str:operation>/<uuid:product_id>/', RemoveCartItemView.as_view(), name='remove_cart_item'),
    path('cart/remove/<str:operation>/', RemoveCartItemView.as_view(), name='remove_cart_items'),
    path("shippings/", ShippingListView.as_view(), name="shipping"),
    path("shippings/<uuid:pk>/", ShippingDetailView.as_view(), name="shipping_detail"),
    # path("completeorder/", complete_order, name="completeorder"),
    # path("confirmorder/", confirm_order, name="confirmorder"), # confirmorder 
    # path('cart/', CartListView.as_view(), name='cart-list'), # cart-list
    # path('cart/<int:pk>/', CartDetailView.as_view(), name='cart-detail'), # cart-detail
    path('orders/cart-item/', CartItemListView.as_view(), name='cartitem-list'), # cartitem-list
    path('cart-item/<int:pk>/', CartItemDetailView.as_view(), name='cartitem-detail'), # cartitem-detail
]