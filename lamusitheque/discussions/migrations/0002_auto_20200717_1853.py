# Generated by Django 2.1.5 on 2020-07-17 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discussions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='object_id',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
