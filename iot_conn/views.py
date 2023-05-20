from django.shortcuts import render
from .models import IotSubDev
from iot_device.models import Device,CtrlChannel,Measurement,MetricData
from .serializers import IotSubDevSerializer
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt import authentication
from rest_framework.decorators import action

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from datetime import datetime

# mqtt
import paho.mqtt.client as mqtt
import json
from django.conf import settings

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def on_connect(client, userdata, flags, rc):
    return str(rc)

def on_message(client, userdata, msg):

    print(msg.payload)

    msg = msg.payload
    #devices_pk = userdata
    #device = Device.objects.get(id=devices_pk)
    #ctrlchannel = device.ctrlchannel_set.all()
    
    params = json.loads(msg)

    for tmp in params:
        if tmp =="measurement":
            for dc_tmp in params[tmp]:
                timestamp = datetime.now()
                try:
                    measurement = Measurement(datachannel=dc_tmp['datachannel'],timestamp=timestamp,value=dc_tmp['value'])
                    measurement.save()
                except:
                    pass
        elif tmp =="metricdata":
            for dc_tmp in params[tmp]:
                timestamp = datetime.now()
                ctrlchannel = CtrlChannel.objects.get(id=dc_tmp['ctrlchannel'])
                metricdata = MetricData(ctrlchannel=ctrlchannel,timestamp=timestamp,value=dc_tmp['value'],direction="UP")
                metricdata.save()
        else:
            tmp = "Wrong parameters"
            return tmp
    print("Subscribed is OK.")
    return True


class IotSubDevViewSet(viewsets.ModelViewSet):
    """
    list:
    查询云端订阅设备列表

    create:
    创建云端订阅设备，推荐使用
    无需POST数据即可创建

    retrieve:
    查询云端订阅设备详情

    update:
    更新云端订阅设备

    partial_update:
    更新云端订阅设备部分属性

    destroy:
    删除云端订阅设备

    subscribe:
    加入订阅或者取消订阅
    需要POST数据，sub_choice="SUBSCRIBE",表示加入订阅任务，sub_choice="UNSUBSCRIBE",表示取消订阅任务

    """

    serializer_class = IotSubDevSerializer
    authentication_classes = (authentication.JWTAuthentication,)
    queryset = IotSubDev.objects.all()


    def create(self, request, devices_pk=None):
        device = Device.objects.get(id=devices_pk)
        queryset = {"device":device.id,"device_title":device.title,"owner":self.request.user.id,"topic":devices_pk,"status":"UNSUBSCRIBED"}
        serializer = IotSubDevSerializer(data=queryset)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    def list(self, request, devices_pk=None):
        queryset = IotSubDev.objects.filter(device=devices_pk)
        serializer = IotSubDevSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None,devices_pk=None):
        queryset = IotSubDev.objects.filter(pk=pk, device=devices_pk)
        queryset_tmp = get_object_or_404(queryset, pk=pk)

        serializer = IotSubDevSerializer(queryset_tmp)
        return Response(serializer.data)

    
    @action(detail=False, methods=['post'])
    def subscribe(self, request, devices_pk=None):
        try:
            client = mqtt.Client(client_id=devices_pk,userdata=devices_pk,clean_session=False)
            #20190922 ADD
            #client.username_pw_set(username=settings.MQTT_USERNAME, password=settings.MQTT_PASSWORD)
            #20190922 ADD
            client.on_connect = on_connect
            rc=client.connect(settings.MQTT_HOST,port=1883, keepalive=60)
            print("rc=%d" %(rc))
            if request.method == 'POST':
                # 修改
                sub_choice = request.data['status']
                if sub_choice == "SUBSCRIBE":
                    if rc == 0:
                        client.on_message = on_message
                        client.subscribe(topic=devices_pk,qos=2)
                        client.loop_start()
                        iotsubdev = IotSubDev.objects.get(device=devices_pk)
                        iotsubdev.status = "SUBSCRIBED"
                        iotsubdev.save()
                        info = {"status":"SUBSCRIBED"}
                        print(info)
                        return JSONResponse(info)
                    elif rc == "1":
                        info = {"status":"Connection refused - incorrect protocol version"}
                        return JSONResponse(info)
                    elif rc == "2":
                        info = {"status":"Connection refused - invalid client identifier"}
                        return JSONResponse(info)
                    elif rc == "3":
                        info = {"status":"Connection refused - server unavailable"}
                        return JSONResponse(info)
                    elif rc == "4":
                        info = {"status":"Connection refused - bad username or password"}
                        return JSONResponse(info)
                    elif rc == "5":
                        info = {"status":"Connection refused - not authorised"}
                        return JSONResponse(info)
                    else:
                        info = {"status":"Wrong"}
                        return JSONResponse(info)
                elif sub_choice == "UNSUBSCRIBE":
                    client.unsubscribe(topic=devices_pk)
                    print("UNSUBSCRIBE IS OK!")
                    client.loop_stop()
                    client.disconnect()
                    iotsubdev = IotSubDev.objects.get(device=devices_pk)
                    iotsubdev.status = "UNSUBSCRIBED"
                    iotsubdev.save()
                    info = {"status":"UNSUBSCRIBED"}
                    return JSONResponse(info)
                else:
                    info = {"status":"The post data is wrong."}
                    return JSONResponse(info)
            else:
                return JSONResponse(["no content"])
        except:
                return JSONResponse(["exception"])

#系统启动后，会把SUBSCRIBED状态的设备加入订阅进程
def init_subscribe():
    iotsubdevs = IotSubDev.objects.all()
    #client = mqtt.Client(client_id=devices_pk,userdata=devices_pk,clean_session=True)
    for iotsubdev in iotsubdevs:
        try:
            devices_pk = iotsubdev.device.id
            client = mqtt.Client()
            #20190922 ADD
            #client.username_pw_set(username=settings.MQTT_USERNAME, password=settings.MQTT_PASSWORD)
            #20190922 ADD
            client.on_connect = on_connect
            client.on_message = on_message
            rc=client.connect(settings.MQTT_HOST,port=1883, keepalive=60)
            print("rc=%d" %(rc))
            if (rc == 0 and iotsubdev.status == "SUBSCRIBED"):
                client.subscribe(topic=str(devices_pk),qos=0)
                client.loop_start()
            else:
                pass

        except:
                pass

init_subscribe()

'''
注意: Linux终端中必须"添加转义字符 -> \, json数据中的"需要写为\"， 否则on_message回调函数中会出问题, 即json数据解析错误
mosquitto_pub -t "dd646cfa-a678-4d6f-a0ae-8368ee957e06" -m "{\"metricdata\":[{\"ctrlchannel\":\"d24cf0d3-505c-4130-ab29-63a792013936\",\"value\":555}]}"
訂閱設備
mosquitto_sub  -t "d24cf0d3-505c-4130-ab29-63a792013936" 
'''
