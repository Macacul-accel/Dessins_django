from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
from .models import Product, Category, Order
from .filters import OrderFilter


class LatestProductList(APIView):
    def get(self, request, format=None):
        products = Product.objects.order_by('-date_added')[0:4]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetail(APIView):
    def get(self, request, category_slug, product_slug, format=None):
        product = get_object_or_404(
            Product.objects.select_related('category'),
            category__slug=category_slug,
            slug=product_slug
        )
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
class CategoryDetail(APIView):
    def get(self, request, category_slug, format=None):
        category = get_object_or_404(
            Category.objects.prefetch_related('products'),
            slug=category_slug
        )
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
class SearchProduct(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.data.get('query', '').strip()

        if not query:
            return Product.objects.all().order_by('-date_added')

        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
            ).order_by('-date_added')
    
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        qs = super().get_queryset
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    @action(
        detail=False,
        methods=['GET'],
        url_path='user-orders',
        permission_classes=[IsAuthenticated]
    )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)