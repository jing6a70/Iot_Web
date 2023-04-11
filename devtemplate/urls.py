from django.urls import re_path as url
from django.urls import path,include
from rest_framework import routers

from .views import DevTemplateViewSet

router = routers.DefaultRouter()

# 定义文本路径
fpath =r''
router.register(r'', DevTemplateViewSet,basename='devtemplates')

urlpatterns = [
    url(r'^', include(router.urls)),
]
