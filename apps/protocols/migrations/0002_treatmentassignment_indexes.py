# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('protocols', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='treatmentassignment',
            index=models.Index(fields=['status', '-created_at'], name='treatment_a_status_467ee7_idx'),
        ),
        migrations.AddIndex(
            model_name='treatmentassignment',
            index=models.Index(fields=['start_date'], name='treatment_a_start_d_a5e9f8_idx'),
        ),
    ]
