from products.models import Product, Group, SubGroup, Category
from common.serializers import BaseModelSerializer
from rest_framework import serializers


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
    image_url = serializers.SerializerMethodField('get_image_url')

    class Meta(BaseModelSerializer.Meta):
        model = Product

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)


class ReadProductSerializer(BaseModelSerializer):
    """

    """
    group = GroupSerializer(many=True, read_only=True)
    subgroup = SubGroupSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Product
