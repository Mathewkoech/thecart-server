from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import api_view
# from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.registration.views import VerifyEmailView, RegisterView
from dj_rest_auth.views import LoginView
# from dj_rest_auth.app_settings import create_token
from thecart_auth.serializers import (
    UserSerializer, RegisterNonAdminUserSerializer
)
from common.jwt import get_jwt
# from common.permissions import IsOpsAdmin
from thecart_auth.models import User
from common.views import BaseDetailView
# email resend verification
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from allauth.account.utils import send_email_confirmation
from rest_framework.views import APIView

from rest_framework.decorators import api_view, permission_classes
from allauth.account.models import EmailAddress
import datetime
from django.utils import timezone
from uuid import uuid4 as uuid


# Create your views here.
@api_view()
def null_view(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)

class RegisterUSerView(RegisterView):
    serializer_class = RegisterNonAdminUserSerializer

class TokenBasedLoginView(LoginView):
    """
    A custom login view for users that require token based login
    """

    def login(self):
        self.user = self.serializer.validated_data["user"]
        self.token = create_token(self.token_model, self.user, self.serializer)

    def get_response(self):
        serializer = TokenSerializer(
            instance=self.token, context={"request": self.request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersListView(GenericAPIView):
    """
    Users list view
    """

    model = User
    serializer_class = UserSerializer
    read_serializer_class = UserSerializer

    def get_read_serializer_class(self):
        if self.read_serializer_class is not None:
            return self.read_serializer_class
        return self.serializer_class

    def get_queryset(self, request):
        queryset = []
        role = request.GET.get("role", None)
        if role is not None:
           queryset = self.model.objects.filter(role=role, is_deleted=False)
        else:
           queryset = self.model.objects.filter(is_deleted=False) 
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


class UserDetailView(BaseDetailView):
    """
    Update, Delete, or View a User
    """

    model = User
    serializer_class = UserSerializer

    def get_object(self, request, pk):
        if pk is not None:
            return get_object_or_404(User, pk=pk)
        return request.user

    def get(self, request, pk=None):
        return super().get(request, pk)

    def put(self, request, pk=None):
        return super().put(request, pk)

    def delete(self, request, pk=None):
        item = self.get_object(request, pk)
        if hasattr(item, "is_deleted"):
            item.is_deleted = True
            item.deleted_at = datetime.datetime.now(tz=timezone.utc)
            item.modified_by = request.user
            new_email = str(item.id)+"@deleted.com"
            item.email = new_email
            email_address = EmailAddress.objects.get(user__exact=item.id)
            email_address.email = new_email
            item.is_active = False
            email_address.save()
            item.save()
        else:
            item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from thecart_auth.models import Profile
from ordering.models import Order,Shipping
from products.models import Product
@api_view(["GET"])
def migrate_stuff(request):
    for item in Product.objects.all():
        item.base_uuid_id = item.user.uuid 

    return Response({'item':"item"}, status=status.HTTP_200_OK)     