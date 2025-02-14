import stripe
from decouple import config

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, filters
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

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
    queryset = Product.objects.select_related('category').all().order_by('-date_added')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']
    pagination_class = LimitOffsetPagination

stripe.api_key = config('STRIPE_SECRET_KEY')

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    @action(detail=True, methods=['POST'])
    def create_payment(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.StatusChoices.PENDING:
            return Response({'error': "Veuillez nous contacter pour régler le problème"}, status=400)
        
        data = request.POST
        shipping_info = {
            'name': data.get('name'),
            'address': {
                'line1': data.get('address'),
                'postal_code': data.get('postal_code'),
                'city': data.get('city'),
                'country': data.get('country')
            }
        }
        order.shipping_details = shipping_info
        order.save()

        serializer = self.get_serializer(order)
        total_price = serializer.data['total_price']
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),
                currency='eur',
                metadata={'order_id': str(order.order_id)},
                shipping=shipping_info,
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return Response({'clientSecret': intent['client_secret']}, status=200)
        except Exception as e:
            return Response({'error': e}, status=400)
    
    @action(detail=False, methods=['GET'])
    def check_pending_order(self, request):
        """Check if the user already has an order but has not paid yet"""
        pending_order = Order.objects.filter(user=request.user, status=Order.StatusChoices.PENDING).first()
        if not pending_order:
            return Response({'order_id': None})
        return Response({'order_id': pending_order.order_id})
    
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    endpoint = config('STRIPE_WEBHOOK_SK')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint
        )
    except ValueError as e:
        return Response({'error': e}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': e}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
                order.status = 'Confirmée'
                order.payment_token = payment_intent['id']
                order.save()
            except Order.DoesNotExist:
                return Response({'error': 'Commande non trouvée'})
        else:
            return Response({'error': 'Commande introuvable'})
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        error_message = payment_intent['last_payment_error']['message']
        return Response({'error': error_message})
    
    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        order_id = charge['metadata'].get('order_id')
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
                order.status = 'Annulée'
                order.save()
            except Order.DoesNotExist:
                return Response({'error': 'Commande non trouvée'})

    else:
        print(f"event non pris en compte {event['type']}")
    return Response({'status': 'success'}, status=200)