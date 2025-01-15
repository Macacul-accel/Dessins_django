from django.urls import path
from rest_framework.routers import DefaultRouter

from product import views


urlpatterns = [
    path('latest-product/', views.LatestProductList.as_view()),
    path('products/search/', views.SearchProduct.as_view()),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('products/<slug:category_slug>/', views.CategoryDetail.as_view()),
]

router = DefaultRouter()
router.register('orders', views.OrderViewSet)
urlpatterns += router.urls