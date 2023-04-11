from django.db import models
from django.utils.translation import gettext_lazy as _
from iot_device.models import Device

class IotSubDev(models.Model):
    """
    云端订阅设备
    topic:设备ID

    """
    SUBSCRIBED = 'SUBSCRIBED'
    UNSUBSCRIBED = 'UNSUBSCRIBED'
    SUB_CHOICES = (
        (SUBSCRIBED, 'SUBSCRIBED'),
        (UNSUBSCRIBED, 'UNSUBSCRIBED'),
    )

    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    device_title = models.CharField(max_length=80, blank=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    topic = models.CharField(max_length=40, blank=True)
    status =  models.CharField(
        max_length=20,
        choices=SUB_CHOICES,
        default=UNSUBSCRIBED,
    )

    def __str__(self):  # Python 3: def __str__(self):
        return self.topic
