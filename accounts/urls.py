from django.urls import re_path as url
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'myprofile', views.MyProfileViewSet, basename='myprofile')

urlpatterns = [
    url(r'^', include(router.urls)),
]
