from django.db import models
from common.models import TimeStampedModelMixin, FlaggedModelMixin
from thecart_auth.models import User
from common.utils import generate_random_number
from products.models import Product


class Order(FlaggedModelMixin, TimeStampedModelMixin):
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_order", null=True
    )
    order_number = models.CharField(
        blank=False,
        null=False,
        default=generate_random_number,
        unique=True,
        max_length=30,
    )
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"
    PENDING = "Pending"
    SHIPPED = "Shipped"
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (SHIPPED, "Shipped"),
    )
    ORDER_CHOICES = (
        (CONFIRMED, "confirmed"),
        (NOT_CONFIRMED, "not_confirmed"),
    )
    status = models.CharField(
        blank=False, null=False, choices=STATUS_CHOICES, default=PENDING, max_length=20,
    )
    order_status = models.CharField(
        blank=False, null=True, choices=ORDER_CHOICES, default=NOT_CONFIRMED, max_length=20,
    )
    total = models.DecimalField(max_digits=14, decimal_places=4, null=True)
    discount = models.DecimalField(max_digits=14, decimal_places=4, null=True)
    total_after_discount = models.DecimalField(
        max_digits=14, decimal_places=4, null=True
    )
    items = models.PositiveIntegerField(default=1)
    first_name = models.CharField(max_length=250, blank=True)
    last_name = models.CharField(max_length=250, blank=True)
    email = models.CharField(max_length=250, blank=True)
    phone = models.CharField(max_length=250, blank=True)
    address = models.CharField(max_length=250, blank=True)
    delivered_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rider", null=True
    )
    shipping = models.ForeignKey(
        "Shipping", on_delete=models.CASCADE, related_name="order_shipping", null=True
    )

    def __str__(self):
        return self.first_name + " " + self.last_name + " " + self.order_number

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]


class OrderItem(TimeStampedModelMixin):
    """
    A class definition for an order item.

    """

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=4, null=True)
    price = models.DecimalField(
        max_digits=14, decimal_places=4, editable=False, default=0
    )
    value = models.DecimalField(
        max_digits=14, decimal_places=4, editable=False, default=0
    )
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="order_items", null=False,
    )

    def __str__(self):
        return str(self.order)

    class Meta:
        verbose_name_plural = "Order Items"
        db_table = "order_item"

    def save(self, *args, **kwargs):
        """
        Override default save method to populate value field
        """
        self.price = self.product.price
        self.value = self.price * self.quantity
        return super().save(*args, **kwargs)


class Shipping(FlaggedModelMixin, TimeStampedModelMixin):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_shipping",
    )
    postal_code = models.CharField(max_length=250, blank=True)
    address = models.CharField(max_length=250, blank=True)
    town = models.CharField(max_length=250, blank=True)
    default = models.BooleanField(default=False)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, related_name="order_shipping"
    )

    def __str__(self):
        return self.user

    class Meta:
        db_table = "shipping"



