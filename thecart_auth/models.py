from django.db import models
from uuid import uuid4 as uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser

class User(AbstractBaseUser):
    id = models.UUIDField(default=uuid, primary_key=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    username = models.CharField(_("username"), max_length=150, blank=True, unique=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    # is_ops_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    modified_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="deleted_%(class)s",
    )
