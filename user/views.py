from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware.csrf import get_token

class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']

            res = Response({'success': True})

            res.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
                max_age=600
            )

            res.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
                max_age=86400
            )

            csrf_token = get_token(request)
            res.data['X-CSRFToken'] = csrf_token

            return res

        except KeyError:
            return Response({'success': False, 'error': 'Token generation failed'}, status=400)

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']

            res = Response({'refreshed': True})

            res.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
                max_age=600
            )

            csrf_token = get_token(request)
            res.data['X-CSRFToken'] = csrf_token

            return res
        
        except KeyError:
            return Response({'refreshed': False, 'error': 'Token refresh failed'}, status=400)

        except Exception as e:
            return Response({'refreshed': False, 'error': str(e)}, status=500)

@api_view(['POST'])
def logout(request):
    """
    The front need to send the X-CSRFToken in the headers to logout
    """
    try:
        res = Response({'success': True})
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)