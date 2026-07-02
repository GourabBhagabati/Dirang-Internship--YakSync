# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hormones', '0002_hormonerelease_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='HormoneSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('release_date', models.DateField()),
                ('release_time', models.TimeField()),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('released', 'Released'), ('cancelled', 'Cancelled')], default='scheduled', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hormone_schedules', to='animals.animal')),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hormone_schedules', to=settings.AUTH_USER_MODEL)),
                ('reservoir', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='hormones.hormonereservoir')),
            ],
            options={
                'verbose_name': 'Hormone Schedule',
                'verbose_name_plural': 'Hormone Schedules',
                'db_table': 'hormone_schedules',
                'ordering': ['release_date', 'release_time'],
            },
        ),
    ]
