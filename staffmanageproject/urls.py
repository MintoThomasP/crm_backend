"""
URL configuration for staffmanageproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.urls import path, re_path as url
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="PROJECT MANAGE API",
        default_version='v1',
        description="Welcome to the Spog website documentation page",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets234.local"),
        license=openapi.License(name=""),
    ),
    public=False,
    permission_classes=(permissions.IsAuthenticated,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-default/', include('app_default.urls')),
    path('api-project/', include('app_project.urls')),
    path('api-staff/', include('app_staff.urls')),
    path('api-client/', include('app_client.urls')),
    path('api-login/', include('app_login.urls')),
    path('api-sale/', include('app_sale.urls')),
    path('api-site/', include('app_site.urls')),
    path('api-report/', include('app_report.urls')),
    path('api-company/', include('app_company.urls')),
    path('api-category/', include('app_category.urls')),
    path('api-notes/', include('app_notes.urls')),
    path('api-enquiry/', include('app_enquiry.urls')),
    path('api-basic/', include('app_basic.urls')),
    path('api-todo/', include('app_todo.urls')),
    path('api-credential/', include('app_credential.urls')),
    path('api-website-email/', include('app_website_email.urls')),
    path('api-vendor/', include('app_vendor.urls')),
    path('api-noti/', include('app_firebase.urls')),
    path('api-blog/', include('app_blog.urls')),
    path('api-accounting/', include('app_accounting.urls')),
    path('api-client-portal/', include('app_client_portal.urls')),
    path('swagger-json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger<str:format>', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    # url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT,}),
]
# 1. Fallback for Static Files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 2. Add this conditional check to serve Media Uploads during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

admin.site.site_url = '/swagger/'
