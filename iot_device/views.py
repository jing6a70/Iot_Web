from django.shortcuts import render
from .models import Device,CtrlChannel,MetricData, DataChannel, Measurement
from .serializers import DeviceSerializer,CtrlChannelSerializer,MetricDataSerializer,DataChannelSerializer, MeasurementSerializer

from django.shortcuts import get_object_or_404

from rest_framework import status,viewsets
from rest_framework.response import Response
from rest_framework_simplejwt import authentication

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from rest_framework.decorators import action

import json
import paho.mqtt.publish as publish
from django.conf import settings


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class DeviceViewSet(viewsets.ModelViewSet):
    """
    list:
    查询设备列表

    create:
    创建设备

    retrieve:
    查询设备详情

    update:
    更新设备

    partial_update:
    更新设备部分属性

    destroy:
    删除设备

    createDevByTpl:
    根据提供的模板创建设备及相关的数据、控制通道

    """

    serializer_class = DeviceSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    queryset = Device.objects.all()

    def perform_create(self, serializer):
    	serializer.save(owner=self.request.user)

    def list(self, request,):
        queryset = Device.objects.filter(owner=request.user).order_by('-created')
        self.check_object_permissions(request,Device)
        serializer = DeviceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Device.objects.filter(owner=request.user)
        queryset_tmp = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request,Device)
        serializer = DeviceSerializer(queryset_tmp)
        return Response(serializer.data)


class CtrlChannelViewSet(viewsets.ModelViewSet):
    """
    list:
    查询控制通道列表

    create:
    创建控制通道

    retrieve:
    查询控制通道详情

    update:
    更新控制通道

    partial_update:
    更新控制通道部分属性

    destroy:
    删除控制通道

    """

    serializer_class = CtrlChannelSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    queryset = CtrlChannel.objects.all()

    def list(self, request, devices_pk=None):
        queryset = CtrlChannel.objects.filter(device=devices_pk)
        # serializer = CtrlChannelSerializer(queryset, many=True)
        # return Response(serializer.data)
        tmplist = []
        for dl in queryset:
            tmplist.append({"id":dl.id,"device":dl.device.id,"title":dl.title,"datatype":dl.datatype,"device_title":dl.device.title})
        return JSONResponse(tmplist)

    def retrieve(self, request, pk=None, devices_pk=None):
        queryset = CtrlChannel.objects.filter(pk=pk, device=devices_pk)
        queryset_tmp = get_object_or_404(queryset, pk=pk)

        serializer = CtrlChannelSerializer(queryset_tmp)
        return Response(serializer.data)



class MetricDataViewSet(viewsets.ModelViewSet):
    """
    list:
    查询数据点列表

    create:
    提交数值数据
    如果方向为DOWN，支持MQTT发布消息

    retrieve:
    查询数值数据详情

    update:
    更新数值数据，不建议使用

    partial_update:
    更新数值数据部分属性，不建议使用

    destroy:
    删除数值单位
    """

    serializer_class = MetricDataSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    queryset = MetricData.objects.all()

    # 重写create 方法 添加指令下发功能
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            try:
                if request.data["direction"] == "DOWN":
                    payload = json.dumps(request.data)
                    ctrlchannels_id = request.data["ctrlchannel"]
                    publish.single(ctrlchannels_id, payload,hostname=settings.MQTT_HOST)
            except:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, devices_pk=None,ctrlchannels_pk=None):
        queryset = MetricData.objects.filter(ctrlchannel=ctrlchannels_pk)
        serializer = MetricDataSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, devices_pk=None,ctrlchannels_pk=None):
        queryset = MetricData.objects.filter(pk=pk,ctrlchannel=ctrlchannels_pk)
        queryset_tmp = get_object_or_404(queryset, pk=pk)

        serializer = MetricDataSerializer(queryset_tmp)
        return Response(serializer.data)


class DataChannelViewSet(viewsets.ModelViewSet):
    """
    list:
    查询数据通道列表

    create:
    创建数据通道

    retrieve:
    查询数据通道详情

    update:
    更新数据通道

    partial_update:
    更新数据通道部分属性

    destroy:
    删除数据通道

    """
    serializer_class = DataChannelSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    queryset = DataChannel.objects.all()

    def list(self, request, devices_pk=None):
        queryset = DataChannel.objects.filter(device=devices_pk)
        serializer = DataChannelSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, devices_pk=None):
        queryset = DataChannel.objects.filter(pk=pk, device=devices_pk)
        queryset_tmp = get_object_or_404(queryset, pk=pk)

        serializer = DataChannelSerializer(queryset_tmp)
        return Response(serializer.data)



#以下操作的是mongodb
class MeasurementViewSet(viewsets.ModelViewSet):
    """
    list:
    查询设备上传数据列表

    create:
    提交设备上传数据

    retrieve:
    查询设备上传数据详情
    id为mongodb的文档_id

    update:
    更新设备上传数据，不建议使用
    id为mongodb的文档_id

    partial_update:
    更新设备上传数据部分属性，不建议使用
    id为mongodb的文档_id

    destroy:
    删除设备上传数据
    id为mongodb的文档_id

    latestvalue:
    查询最新的设备上传数据

    range:
    查询某一时间段的设备上传数据
    时间字符串：2019-04-04 00:29:00；时间格式：%Y-%m-%d %H:%M:%S;POST:from_date = 2019-04-04 00:29:00
         to_date = 2019-04-05 00:29:00;date_format = %Y-%m-%d %H:%M:%S。

    """

    serializer_class = MeasurementSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    queryset = Measurement.objects.all()


    def list(self, request, devices_pk=None,datachannels_pk=None):
        queryset = Measurement.objects(datachannel=datachannels_pk)
        serializer = MeasurementSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request,devices_pk=None,datachannels_pk=None):
        try:
            if request.method == 'POST':
                value = float(request.data['value'])
                timestamp = datetime.now()
                measurement_obj = Measurement(datachannel=datachannels_pk,timestamp=timestamp,value=value)
                measurement_obj.save()
                info = {'datachannel':datachannels_pk,'timestamp':timestamp,'value':value}
                return JSONResponse(info)

            else:
                return JSONResponse(["no content"])
        except:
                return JSONResponse(["exception"])


    @action(detail=False, methods=['get'])
    #@list_route(methods=['get'])
    def latestvalue(self, request, devices_pk=None,datachannels_pk=None):

        try:
            if request.method == 'GET':
                queryset = Measurement.objects(datachannel=datachannels_pk)
                serializer = MeasurementSerializer(queryset, many=True)
                return Response(serializer.data[-1])
            else:
                return JSONResponse(["no content"])
        except:
                return JSONResponse(["exception"])

    @action(detail=False, methods=['get'])
    #@list_route(methods=['get'])
    def latestoneday(self, request, devices_pk=None,datachannels_pk=None):

        try:
            if request.method == 'GET':
                end_date = datetime.now()
                start_date = end_date - timedelta(days=1)
                queryset = Measurement.objects(timestamp__gte=start_date,timestamp__lte=end_date,datachannel=datachannels_pk)
                serializer = MeasurementSerializer(queryset, many=True)
                return Response(serializer.data)
            else:
                return JSONResponse(["no content"])
        except:
                return JSONResponse(["exception"])


    @action(detail=False, methods=['get'])
    #@list_route(methods=['get'])
    def range(self, request, devices_pk=None,datachannels_pk=None):
        #数据的查询
        #时间字符串：2019-04-04 00:29:00
        #时间格式：%Y-%m-%d %H:%M:%S
        try:
            if request.method == 'POST':
                req_from_date = request.data['from_date']
                req_to_date  = request.data['to_date']
                req_date_format = request.data['date_format']
                #strptime 把时间转换为时间戳
                start_date = datetime.strptime(req_from_date,req_date_format)
                end_date = datetime.strptime(req_to_date,req_date_format)
                queryset = Measurement.objects(timestamp__gte=start_date,timestamp__lte=end_date,datachannel=datachannels_pk)
                serializer = MeasurementSerializer(queryset, many=True)
                return Response(serializer.data)
            else:
                return JSONResponse(["no content"])
        except:
                return JSONResponse(["exception"])

