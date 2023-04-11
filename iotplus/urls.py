"""iotplus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path,include
from django.urls import re_path as url

from django.conf import settings

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

schema_view = get_schema_view (
    openapi.Info(
        title="接口文档平台",  # 必传
        default_version="v1",  # 必传
        description="文档描述",
        terms_of_service="",
        contact=openapi.Contact(email="mhhcode@mhhcode.com"),
        license=openapi.License(name="BSD LICENSE")
    ),
    public=True,
    # permission_classes=(permissions.)  # 权限类
)

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView 
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^devtemplate/', include('devtemplate.urls')), 
    url(r"^docs/", include_docs_urls(title="My API title")),  # 出错
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    url(r'^token-api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token-api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^token-api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    url(r'^rest-auth/', include('rest_auth.urls')), 

    url(r'^myprofile/', include('accounts.urls')),
    url(r'^device/', include('iot_device.urls')), 

    url(r'^iotsub_dev/', include('iot_conn.urls')),
]

#static
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static( settings.STATIC_URL, document_root=settings.STATIC_ROOT )
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
