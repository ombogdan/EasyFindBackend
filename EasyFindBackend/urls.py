# EasyFindBackend/urls.py
from django.contrib import admin
from django.urls import path, include
from myapp.views import NearbyOrganizationsView, NearbyServicesView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('api/organizations/nearby/', NearbyOrganizationsView.as_view(), name='nearby_organizations'),
    path("api/nearby-services/", NearbyServicesView.as_view(), name="nearby-services"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
