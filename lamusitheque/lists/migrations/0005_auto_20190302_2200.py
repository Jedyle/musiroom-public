# Generated by Django 2.1.5 on 2019-03-02 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0004_auto_20190302_1254'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listobj',
            old_name='owner',
            new_name='user',
        ),
    ]