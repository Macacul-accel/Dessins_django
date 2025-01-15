from django_filters import FilterSet, DateFilter
from .models import Product, Order

class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['iexact', 'icontains'],
            'description': ['iexact', 'icontains'],
            'price': ['iexact', 'lt', 'gt', 'range'],
        }

class OrderFilter(FilterSet):
    created_at = DateFilter(field_name='created_at__date')

    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at': ['lt', 'gt', 'exact'],
        }