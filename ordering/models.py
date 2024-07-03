from django.db import models
from common.models import TimeStampedModelMixin, FlaggedModelMixin
from thecart_auth.models import User
from common.utils import generate_random_number
from products.models import Product
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Shipping(FlaggedModelMixin, TimeStampedModelMixin):
    """
    Represents a user's shipping address.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Shipping Address"

class CartItem(models.Model):
    """
    Represents an item added to a user's cart.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity}x {self.product}"


class Order(TimeStampedModelMixin, FlaggedModelMixin):
    """
    Represents a confirmed order placed by a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipping', 'Shipping'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_address = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method_choices = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ]
    payment_method = models.CharField(max_length=50, choices=payment_method_choices, default='mpesa')
    contact_email = models.EmailField(default=None, null=True, blank=True)
    cart = models.ForeignKey(CartItem, on_delete=models.CASCADE, default=None, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, default=None, null=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return f"Order {self.id} - {self.status}"


class OrderItem(TimeStampedModelMixin):
    """
    """
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} - {self.order}"

