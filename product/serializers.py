from rest_framework import serializers

from .models import Category, Product

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'category_name',
            'get_absolute_url',
            'description',
            'price',
            'get_image',
            'get_thumbnail',
        )

class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'get_absolute_url',
            'products',
        )