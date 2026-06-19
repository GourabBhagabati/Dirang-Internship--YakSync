# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hormones', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='hormonerelease',
            index=models.Index(fields=['-timestamp'], name='hormone_rel_timesta_4e861a_idx'),
        ),
    ]
