# Generated by Django 2.1.5 on 2020-12-12 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0006_auto_20201212_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active'),
        ),
    ]