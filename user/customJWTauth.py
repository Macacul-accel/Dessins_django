from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Set the Token in the headers from the cookies
        """
        access_token = request.COOKIES.get('access_token')
        if access_token:
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        return super().authenticate(request)