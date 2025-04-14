# EasyFindBackend/urls.py
from django.contrib import admin
from django.urls import path, include

from myapp.views import NearbyOrganizationsView, NearbyServicesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('api/organizations/nearby/', NearbyOrganizationsView.as_view(), name='nearby_organizations'),
    path("api/nearby-services/", NearbyServicesView.as_view(), name="nearby-services"),
]
