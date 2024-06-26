from django.urls import path
from products.views import (
    ProductListView,
    ProductDetailView,
    GroupListView,
    GroupDetailView,
    SubGroupListView,
    SubGroupDetailView,
    CategoryListView,
    CategoryDetailView,
)

app_name = "products"
urlpatterns = [
    path("", ProductListView.as_view(), name="products"),
    path(
        "products/<str:slug>/", ProductDetailView.as_view(),
        name="product_detail"
    ),
    path("groups/", GroupListView.as_view(), name="groups"),
    path("groups/<uuid:pk>/", GroupDetailView.as_view(), name="groups_detail"),
    path("subgroups/", SubGroupListView.as_view(), name="subgroups"),
    path("subgroups/<uuid:pk>/", SubGroupDetailView.as_view(),
        name="subgroups_detail"
    ),
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(),
        name="categories_detail"
    ),
]
