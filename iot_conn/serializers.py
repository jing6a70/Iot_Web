from rest_framework import serializers
from .models import IotSubDev

class IotSubDevSerializer(serializers.ModelSerializer):

    class Meta:
        model = IotSubDev
        fields = ('id','device','device_title','owner','topic','status')
