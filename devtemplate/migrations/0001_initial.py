# Generated by Django 4.1.7 on 2023-04-07 07:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DevTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=80)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('img', models.ImageField(blank=True, default='upload/none.jpg', upload_to='image')),
                ('device_type', models.CharField(blank=True, max_length=40)),
                ('is_custom_registered', models.BooleanField(default=False)),
                ('protocal_type', models.CharField(choices=[('MQTT', 'MQTT'), ('HTTP', 'HTTP'), ('CoAP', 'CoAP')], default='HTTP', max_length=200)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
