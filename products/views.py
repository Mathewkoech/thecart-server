from django.shortcuts import render
from common.views import (
    BaseDetailView,
    BaseListView,
    ImageBaseDetailView,
    ImageBaseListView,
)
from products.models import Product, Group, SubGroup, Category
from products.serializers import (
    ProductSerializer,
    ReadProductSerializer,
    GroupSerializer,
    SubGroupSerializer,
    ReadSubGroupSerializer,
    CategorySerializer,
    ReadCategorySerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FileUploadParser
from uuid import UUID

from rest_framework.parsers import MultiPartParser, FormParser

class ProductListView(ImageBaseListView):
    """
    """
    # permission_classes = [AllowAny]
    model = Product
    serializer_class = ProductSerializer
    read_serializer_class = ReadProductSerializer
    parser_classes = [MultiPartParser, FormParser]  # Ensure parser classes are defined here

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", None)
        group = self.request.GET.get("group", None)
        subgroup = self.request.GET.get("subgroup", None)
        category = self.request.GET.get("category", None)
        # brand = self.request.GET.get("brand", None)
        kwargs = {}
        kwargs_ors = None
        if q is not None:
            kwargs_ors = Q(name__icontains=q)
        if group is not None:
            kwargs['group_id'] = group
        if subgroup is not None:
            kwargs['subgroup_id'] = subgroup
        if category is not None:
            kwargs['category_id'] = category
        # if brand is not None:
        #     kwargs['brand_id'] = brand

        if len(kwargs) > 0 and kwargs_ors is not None:
            self.filter_object = self.filter_object & (kwargs_ors) & (Q(**kwargs))
            queryset = self.model.objects.filter(self.filter_object)
        elif kwargs_ors is not None:
            self.filter_object = self.filter_object & (kwargs_ors)
            queryset = self.model.objects.filter(self.filter_object)
        elif len(kwargs) > 0:
            self.filter_object = self.filter_object & (Q(**kwargs))
            queryset = self.model.objects.filter(self.filter_object)
        else:
            queryset = queryset
        return queryset.select_related("group", "category", "subgroup").distinct()

    def get(self, request):
        all_status = request.GET.get("all", None)
        if all_status is not None:
            queryset = self.get_queryset()
            serializer = self.get_read_serializer_class()(
                queryset, many=True, context={"request": request}
            )
            return Response(serializer.data)
        else:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            serializer = self.get_read_serializer_class()(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
    @permission_classes([IsAuthenticated])
    def post(self, request):
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            slug = request.data.get("name")
            slug = slug.replace("/", " ")
            slug = slug.replace("&", "and")
            slug = slug.replace(",", "")
            slug = slug.replace(" ", "-")
            slug = slug.lower()
            user = request.user
            image = request.FILES["image"] if "image" in request.FILES else None
            serializer.save(created_by=user, slug=slug, image=image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(ImageBaseDetailView):
    model = Product
    serializer_class = ProductSerializer
    read_serializer_class = ReadProductSerializer

    def get(self, request, pk=None):
        return super().get(request, pk)

    def put(self, request, pk=None):
        parser_classes = [MultiPartParser]
        item = self.get_object(request, pk)
        serializer = self.get_serializer_class()(
            item, data=request.data, partial=True, context={'request':request}
        )
        if serializer.is_valid():
            serializer.save(modified_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        return super().delete(request, pk)


class GroupListView(ImageBaseListView):
    model = Group
    serializer_class = GroupSerializer
    read_serializer_class = GroupSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", None)
        kwargs = {}
        if q is not None:
            kwargs["name__icontains"] = q
        if len(kwargs) > 0:
            queryset = self.model.objects.filter(**kwargs)
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            # slug = name.replace("/", " ").replace("&", "and").replace(",", "").replace(" ", "-").lower()
            serializer.save(name=name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetailView(ImageBaseDetailView):
    """
    """

    model = Group
    serializer_class = GroupSerializer
    read_serializer_class = GroupSerializer
    permission_classes = [AllowAny]


class SubGroupListView(ImageBaseListView):
    permission_classes = [AllowAny]
    model = SubGroup
    serializer_class = SubGroupSerializer
    read_serializer_class = ReadSubGroupSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        subgroup_name = self.request.GET.get("name", None)
        group = self.request.GET.get("group", None)
        if group is not None:
            queryset = self.model.objects.filter(group__id=group)
        if subgroup_name is not None:
            self.filter_object = Q(name__contains=subgroup_name)
            queryset = self.model.objects.filter(self.filter_object)
        return queryset

    def post(self, request):
        """
        """
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid(self):
            slug = request.data.get("name")
            slug = slug.replace("/", " ")
            slug = slug.replace("&", "and")
            slug = slug.replace(",", "")
            slug = slug.replace(" ", "-")
            slug = slug.lower()
            serializer.save(slug=slug,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubGroupDetailView(ImageBaseDetailView):
    """
    """

    permission_classes = [AllowAny]
    model = SubGroup
    serializer_class = SubGroupSerializer
    read_serializer_class = ReadSubGroupSerializer


class CategoryListView(ImageBaseListView):
    permission_classes = [AllowAny]
    model = Category
    serializer_class = CategorySerializer
    read_serializer_class = ReadCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_name = self.request.GET.get("name", None)
        if category_name is not None:
            self.filter_object = Q(name__contains=category_name)
            queryset = self.model.objects.filter(self.filter_object)
        return queryset

    def post(self, request):
        """
        """
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid(self):
            slug = request.data.get("name")
            slug = slug.replace("/", " ")
            slug = slug.replace("&", "and")
            slug = slug.replace(",", "")
            slug = slug.replace(" ", "-")
            slug = slug.lower()
            serializer.save(slug=slug,)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(ImageBaseDetailView):
    """
    """

    permission_classes = [AllowAny]
    model = Category
    serializer_class = CategorySerializer
    read_serializer_class = ReadCategorySerializer


# def update_item_price(request):
#     calculate_item_prices.delay()
#     return Response(status=status.HTTP_200_OK)
