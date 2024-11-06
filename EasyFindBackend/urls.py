# myproject/urls.py

from django.contrib import admin
from django.urls import path, include  # Додайте 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # Включіть URL вашого додатку
]
