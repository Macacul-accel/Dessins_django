from django.urls import path, include
from .views import logout

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('logout/', logout),
]