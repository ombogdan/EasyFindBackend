# myapp/serializers.py
from rest_framework import serializers
from .models import ClientUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = ['id', 'email']
