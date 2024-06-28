from django.contrib import admin
# admin.py
from django.contrib import admin
from .models import Product, Group, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'availability', 'brand', 'available')
    search_fields = ('name', 'brand', 'slug')
    list_filter = ('availability', 'brand', 'category', 'group', 'subgroup')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Product, ProductAdmin)
admin.site.register(Group)
admin.site.register(Category)

