from django_filters import FilterSet
from .models import Order

class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
        }