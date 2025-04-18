# myapp/views.py
import random
from django.core.paginator import Paginator
from rest_framework import viewsets
from .models import ClientUser, ServiceType, Employee
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from myapp.models import Organization
from math import radians, cos, sin, asin, sqrt
from django.http import JsonResponse

User = get_user_model()

def haversine(lon1, lat1, lon2, lat2):
    # Радіус Землі в км
    R = 6371.0

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    distance = R * c
    return distance

class UserViewSet(viewsets.ModelViewSet):
    queryset = ClientUser.objects.all()
    serializer_class = UserSerializer

    # Перевизначимо метод створення для створення користувача з паролем
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = ClientUser.objects.create_user(
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
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                "205264277767-pero3rub5m4ok98iv086dvhecdunjlg1.apps.googleusercontent.com"
            )

            email = idinfo['email']
            name = idinfo.get('name', '')
            name_parts = name.strip().split(' ', 1)

            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )

            if not created and not user.first_name:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NearbyOrganizationsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        lat = request.data.get('latitude')
        lon = request.data.get('longitude')

        if lat is None or lon is None:
            return Response({'error': 'Missing latitude or longitude'}, status=400)

        lat = float(lat)
        lon = float(lon)

        nearby_orgs = []
        for org in Organization.objects.all():
            if org.latitude and org.longitude:
                distance = haversine(lon, lat, org.longitude, org.latitude)
                if distance <= 20:
                    nearby_orgs.append({
                        'id': org.id,
                        'name': org.name,
                        'description': org.description,
                        'image': request.build_absolute_uri(org.image.url) if org.image else None,
                        'latitude': org.latitude,
                        'longitude': org.longitude,
                        'address': org.address,
                        'phone': org.phone,
                        'distance_km': round(distance, 2),
                    })

        return Response({'results': nearby_orgs})

class NearbyServicesView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params.get("latitude", 0))
            lon = float(request.query_params.get("longitude", 0))
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except ValueError:
            return Response({"error": "Invalid latitude, longitude, or pagination"}, status=400)

        services_with_distance = []
        if lat and lon:
            for org in Organization.objects.all():
                distance = haversine(lat, lon, org.latitude, org.longitude)
                for service in org.services.all():
                    services_with_distance.append({
                        "id": service.id,
                        "name": service.name,
                        "description": service.description,
                        "image": service.image.name if service.image else None,
                        "distance": round(distance, 2),
                        "organization": {
                            "id": org.id,
                            "name": org.name,
                            "latitude": org.latitude,
                            "longitude": org.longitude,
                            "address": org.address,
                            "phone": org.phone,
                            "image": request.build_absolute_uri(org.image.url) if org.image else None,
                        }
                    })
            services_with_distance.sort(key=lambda x: x["distance"])
        else:
            all_services = ServiceType.objects.all()
            services_with_distance = random.sample([
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "image": s.image.name if s.image else None,
                    "distance": None,
                    "organization": {
                        "id": s.organization.id,
                        "name": s.organization.name,
                        "latitude": s.organization.latitude,
                        "longitude": s.organization.longitude,
                        "address": s.organization.address,
                        "phone": s.organization.phone,
                        "image": request.build_absolute_uri(s.organization.image.url) if s.organization.image else None,
                    }
                } for s in all_services
            ], min(len(all_services), page_size * page))

        paginator = Paginator(services_with_distance, page_size)
        paginated = paginator.get_page(page)

        return Response({
            "results": paginated.object_list,
            "page": page,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count
        })

def csrf_failure(request, reason=""):
    return JsonResponse({
        "error": "CSRF verification failed.",
        "reason": reason,
    }, status=403)