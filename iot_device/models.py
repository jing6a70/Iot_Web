from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
# Create your models here.
class Device(models.Model):
    """
    设备模板表

    """
    MQTT = 'MQTT'
    HTTP = 'HTTP'
    #CoAP = 'CoAP'
    PROTOCAL_CHOICES = (
        (MQTT, 'MQTT'),
        (HTTP, 'HTTP'),
        #(CoAP, 'CoAP'),
    )

    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    UNACTIVE = 'UNACTIVE'
    ACTIVE = 'ACTIVE'
    STATUS_CHOICES = (
        (ONLINE, 'ONLINE'),
        (OFFLINE, 'OFFLINE'),
        (UNACTIVE, 'UNACTIVE'),
        (ACTIVE, 'ACTIVE'),
    )


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=80, blank=True)
    description = models.TextField(_(u"Description"), blank=True)
    img = models.ImageField(upload_to='image',default = 'upload/none.jpg', blank=True)
    device_type = models.CharField( max_length=40, blank=True)
    is_custom_registered = models.BooleanField(default=False)
    register_code = models.CharField( max_length=120, blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default=UNACTIVE)
    protocal_type = models.CharField(max_length=20,choices=PROTOCAL_CHOICES,default=HTTP)
    last_online = models.DateTimeField(blank=True,null=True)
    activated = models.DateTimeField(blank=True,null=True)
    updated = models.DateTimeField(_(u"Updated date"), auto_now=True)
    created = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)


    def __str__(self):  # Python 3: def __str__(self):
        return self.title

class CtrlChannel(models.Model):
    """
    设备模板的控制通道，所谓控制通道，就是云端向设备发送的指令，
    控制点接受指令而执行一系列动作；
    因此，控制通道有两个方向，一是云端发送指令，是云端到设备的控制点；
    另外是设备的控制点需要实时向云端发送自身的状态；
    """
    DECIMAL = 'DECIMAL'
    MESSAGE = 'MESSAGE'
    SWITCH = 'SWITCH'
    GPS = 'GPS'
    DATATYPE_CHOICES = (
        (DECIMAL, '数值型'),
        (MESSAGE, '文本型'),
        (SWITCH, '开关型'),
        (GPS, 'GPS型'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device,  on_delete=models.CASCADE)
    title = models.CharField(max_length=80, blank=True)
    datatype = models.CharField(max_length=200,choices=DATATYPE_CHOICES,default=DECIMAL)

    def __str__(self):  # Python 3: def __str__(self):
        return self.title

class MetricData(models.Model):
    """
    控制通道的数值型数据，具有两个方向，UP表示设备上报的状态数据
    DOWN表示设备接收的控制数据
    """
    UP = 'UP'
    DOWN = 'DOWN'
    DIRECTION_CHOICES = (
        (UP, 'UP'),
        (DOWN, 'DOWN'),
    )

    ctrlchannel = models.ForeignKey(CtrlChannel,  on_delete=models.CASCADE)
    value = models.FloatField(blank=True)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES,default=UP)
    timestamp = models.DateTimeField(_(u"timestamp"), auto_now_add=True)
    #只有数据变化时才更新
    def save(self, *args, **kwargs):
        queryset = MetricData.objects.filter(ctrlchannel=self.ctrlchannel,direction='UP')
        if queryset:
            tmp = queryset[len(queryset)-1]
            if((self.value == tmp.value) and (self.direction =='UP')):
                pass
            else:
                super(MetricData, self).save(*args, **kwargs)
        else:
            super(MetricData, self).save(*args, **kwargs)

class DataChannel(models.Model):
    """
    设备模板数据通道，数据通道是设备向云端上传数据的通道；
    上传数据通道有四种数据类型，数值型，文本型，开关型，GPS型
    """
    DECIMAL = 'DECIMAL'
    MESSAGE = 'MESSAGE'
    SWITCH = 'SWITCH'
    GPS = 'GPS'
    DATATYPE_CHOICES = (
        (DECIMAL, '数值型'),
        (MESSAGE, '文本型'),
        (SWITCH, '开关型'),
        (GPS, 'GPS型'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device,  on_delete=models.CASCADE)
    title = models.CharField(max_length=80, blank=True)
    datatype = models.CharField(max_length=200,choices=DATATYPE_CHOICES,default=DECIMAL)

    def __str__(self):  # Python 3: def __str__(self):
        return self.title


#mongodb document
import mongoengine
class Measurement(mongoengine.Document):
    datachannel = mongoengine.UUIDField(binary=False, required=True)
    timestamp = mongoengine.DateTimeField()
    value = mongoengine.FloatField()
    meta = {
        'indexes': [
            'datachannel',
            '$datachannel',  # text index
            '#datachannel',  # hashed index
            {
                'fields': ['timestamp'],
                'expireAfterSeconds': 15552000 #180 day
            }
        ]
    }
