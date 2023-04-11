from django.urls import re_path as url
from django.urls import path,include

from rest_framework_nested  import routers
from .views import DeviceViewSet, CtrlChannelViewSet, MetricDataViewSet, DataChannelViewSet, MeasurementViewSet

from django.conf import settings
from djoser import views

router = routers.SimpleRouter()
router.register(r'devices', DeviceViewSet,basename='iot_device')
#先创建一个路由实例，再注册一个url
#第一级URL


device_router = routers.NestedSimpleRouter(router, r'devices', lookup='devices')
device_router.register(r'ctrlchannels', CtrlChannelViewSet, basename='ctrlchannels')
device_router.register(r'datachannels', DataChannelViewSet, basename='datachannels')

ctrlchannel_router = routers.NestedSimpleRouter(device_router,r'ctrlchannels',lookup='ctrlchannels')
ctrlchannel_router.register(r'metricdata',MetricDataViewSet,basename='metricdata')

datachannel_router = routers.NestedSimpleRouter(device_router,r'datachannels',lookup='datachannels')
datachannel_router.register(r'measurements',MeasurementViewSet,basename='measurements')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(device_router.urls)),
    url(r'^', include(ctrlchannel_router.urls)),
    url(r'^', include(datachannel_router.urls)),
] 
