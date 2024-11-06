# myapp/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer

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
