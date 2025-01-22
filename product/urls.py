from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('orders', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('latest-product/', views.LatestProductList.as_view()),
    path('products/', views.SearchProduct.as_view()),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('products/<slug:category_slug>/', views.CategoryDetail.as_view()),
]
