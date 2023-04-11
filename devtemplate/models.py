from django.db import models
#from django.utils.translation import ugettext_lazy as _ (<v2.2可用)
from django.utils.translation import gettext_lazy as _
import uuid

class DevTemplate(models.Model):
    """
    设备模板表
    """
    MQTT = 'MQTT'
    HTTP = 'HTTP'
    CoAP = 'CoAP'
    PROTOCAL_CHOICES = (
        (MQTT, 'MQTT'),
        (HTTP, 'HTTP'),
        (CoAP, 'CoAP'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField( max_length=80, blank=True)
    description = models.TextField(_(u"Description"), blank=True)
    img = models.ImageField(upload_to='image',default = 'upload/none.jpg', blank=True)
    device_type = models.CharField( max_length=40, blank=True)
    is_custom_registered = models.BooleanField(default=False)
    protocal_type = models.CharField(max_length=200,choices=PROTOCAL_CHOICES,default=HTTP)
    updated = models.DateTimeField(_(u"Updated date"), auto_now=True)
    created = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):  # Python 3: def __str__(self):
        return self.title
