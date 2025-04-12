# myapp/views.py
from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    # Перевизначимо метод створення для створення користувача з паролем
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.create_user(
            email=serializer.validated_data['email'],
            password=request.data['password'],
            user_type=serializer.validated_data['user_type']
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('idToken')
        if not token:
            return Response({'error': 'Missing idToken'}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(),
                                                  "205264277767-pero3rub5m4ok98iv086dvhecdunjlg1.apps.googleusercontent.com")
            email = idinfo['email']
            name = idinfo.get('name', '')

            user, created = User.objects.get_or_create(email=email, defaults={'email': email})
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'email': user.email,
                    'name': user.first_name
                }
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
