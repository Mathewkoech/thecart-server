from products.models import Product, Group, SubGroup, Category
from common.serializers import BaseModelSerializer
from rest_framework import serializers
from django.conf import settings

class GroupSerializer(BaseModelSerializer):
    """
    Group serializer
    """

    class Meta(BaseModelSerializer.Meta):
        model = Group


class SubGroupSerializer(BaseModelSerializer):
    """

    """

    class Meta(BaseModelSerializer.Meta):
        model = SubGroup


class ReadSubGroupSerializer(BaseModelSerializer):
    """

    """
    group = GroupSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = SubGroup


class CategorySerializer(BaseModelSerializer):
    """

    """

    class Meta(BaseModelSerializer.Meta):
        model = Category


class ReadCategorySerializer(BaseModelSerializer):
    """

    """
    group = GroupSerializer(read_only=True)
    subgroup = SubGroupSerializer(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Category


class ProductSerializer(BaseModelSerializer):
    """

    """
    
    # group = GroupSerializer(many=True)
    # category = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), required=False)
    # subgroup = serializers.PrimaryKeyRelatedField(many=True, queryset=SubGroup.objects.all())
    # image_url = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = Product

    def __init__(self, instance=None, data=None, request=None, **kwargs):
        super().__init__(instance, data, **kwargs)


class ReadProductSerializer(BaseModelSerializer):
    """

    """
    group = GroupSerializer(many=True, read_only=True)
    subgroup = SubGroupSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            image_url = obj.image.url
            return f"{settings.MEDIA_URL}{image_url}"
        return None

    class Meta(BaseModelSerializer.Meta):
        model = Product
