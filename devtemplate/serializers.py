from rest_framework import serializers
from .models import DevTemplate

class DevTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DevTemplate
        fields = ('id', 'title', 'description','img','device_type','is_custom_registered','protocal_type','updated','created') 
