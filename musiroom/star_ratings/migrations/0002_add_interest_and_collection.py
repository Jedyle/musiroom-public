# Generated by Django 4.0.4 on 2022-04-30 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('star_ratings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrating',
            name='is_in_collection',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userrating',
            name='is_interested',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userrating',
            name='score',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
