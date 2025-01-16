from django.urls import path, include
from .views import logout, MyTokenObtainPairView, MyTokenRefreshView

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('jwt/create/', MyTokenObtainPairView.as_view(), name='jwt-create'),
    path('jwt/refresh/', MyTokenRefreshView.as_view(), name='jwt-refresh'),
    path('logout/', logout),
]