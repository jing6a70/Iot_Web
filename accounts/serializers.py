from .models import MyProfile
from rest_framework import serializers

class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyProfile
        fields = ('user','phone_num', 'mugshot')
