from django.urls import path,include
from django.urls import re_path as url
from rest_framework_nested import routers
from .views import IotSubDevViewSet

from django.conf import settings


# 导入 iot_device 的router
from iot_device.urls import router
iotsubdev_router = routers.NestedSimpleRouter(router, r'devices', lookup='devices')
iotsubdev_router.register(r'iotsubdevs',IotSubDevViewSet, basename='iotsubdevs' )


urlpatterns = [
    url(r'^', include(iotsubdev_router.urls)),
]
