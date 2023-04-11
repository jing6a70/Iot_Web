from django.contrib import admin
from .models import Device,CtrlChannel,MetricData,DataChannel
# Register your models here.

admin.site.register(Device)
admin.site.register(CtrlChannel)
admin.site.register(MetricData)
admin.site.register(DataChannel)
