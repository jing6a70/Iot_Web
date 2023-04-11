from rest_framework import serializers
from .models import Device,CtrlChannel,MetricData,DataChannel

class DeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ('id','title', 'description','img','device_type','is_custom_registered','register_code','status','protocal_type','last_online','activated','owner','updated','created')

class CtrlChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CtrlChannel
        fields = ('id','device', 'title', 'datatype')

class MetricDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = MetricData
        fields = ('id','ctrlchannel', 'value', 'direction', 'timestamp')

class DataChannelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataChannel
        fields = ('id','device', 'title', 'datatype')


# serializer for Datapoint in mongodb
# Measurement
class MeasurementSerializer(serializers.Serializer):
    datachannel = serializers.UUIDField(format='hex_verbose')
    timestamp =serializers.DateTimeField()
    value = serializers.FloatField()
