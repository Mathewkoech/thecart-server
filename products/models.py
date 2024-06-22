from django.db import models
from thecart_auth.models import User
from common.models import TimeStampedModelMixin, FlaggedModelMixin



class Product(FlaggedModelMixin, TimeStampedModelMixin):
    slug = models.CharField(max_length=250, blank=True, null=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    # buying_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    quantity = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/')
    description = models.TextField(blank=True, null=True)
    INSTOCK = "In Stock"
    OUTOFSTOCK = "Out of Stock"
    AVAILABILITY_CHOICES = (
        (INSTOCK, "In Stock"),
        (OUTOFSTOCK, "Out of Stock"),
    )
    availability = models.CharField(
        blank=False,
        null=False,
        choices=AVAILABILITY_CHOICES,
        default=INSTOCK,
        max_length=20,
    )
    brand = models.CharField(max_length=50, blank=True, null=True)
    available = models.DecimalField(max_digits=14, decimal_places=2, default=1)
    group = models.ManyToManyField("products.Group", blank=True)
    subgroup = models.ManyToManyField("products.SubGroup", blank=True)
    category = models.ManyToManyField("products.Category", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"



class Group(FlaggedModelMixin, TimeStampedModelMixin):
    name = models.CharField(max_length=250, unique=True)
    slug = models.CharField(max_length=250, null=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "groups"


class SubGroup(FlaggedModelMixin, TimeStampedModelMixin):
    name = models.CharField(max_length=250, unique=True)
    slug = models.CharField(max_length=250, null=True, unique=True)
    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "subgroups"
        ordering = ["-created_at"]


class Category(FlaggedModelMixin, TimeStampedModelMixin):
    name = models.CharField(max_length=250)
    slug = models.CharField(max_length=250, null=True)
    group = models.ForeignKey("Group", on_delete=models.CASCADE, null=True)
    subgroup = models.ForeignKey("SubGroup", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "categories"
        ordering = ["-created_at"]


