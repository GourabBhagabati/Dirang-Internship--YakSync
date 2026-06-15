# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
        ('animals', '0001_initial'),
        ('devices', '0001_initial'),
        ('monitoring', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='animal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='animals.animal'),
        ),
        migrations.AddField(
            model_name='alert',
            name='device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts', to='devices.device'),
        ),
        migrations.AddField(
            model_name='alert',
            name='sensor_reading',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='monitoring.sensorreading'),
        ),
        migrations.AddField(
            model_name='alert',
            name='acknowledged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='acknowledged_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts_acknowledged', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='alert',
            name='alert_type',
            field=models.CharField(choices=[('low_hormone', 'Low Hormone Level'), ('device_disconnection', 'Device Disconnection'), ('low_battery', 'Low Battery'), ('abnormal_reading', 'Abnormal Reading'), ('missed_schedule', 'Missed Schedule'), ('temperature', 'Body Temperature'), ('movement', 'Movement Level')], max_length=50),
        ),
        migrations.AlterField(
            model_name='alert',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('acknowledged', 'Acknowledged'), ('resolved', 'Resolved')], default='active', max_length=20),
        ),
        migrations.AlterField(
            model_name='alert',
            name='related_entity_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='alert',
            name='related_entity_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
