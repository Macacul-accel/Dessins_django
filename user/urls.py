from django.urls import path, include
from .views import logout, MyTokenObtainPairView, MyTokenRefreshView, restore_cookies

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('restaure_cookies/', restore_cookies),
    path('jwt/create/', MyTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', MyTokenRefreshView.as_view(), name='jwt-refresh'),
    path('logout/', logout),
]