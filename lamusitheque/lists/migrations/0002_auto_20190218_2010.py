# Generated by Django 2.1.5 on 2019-02-18 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listobj',
            old_name='user',
            new_name='owner',
        ),
        migrations.AlterField(
            model_name='listobj',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last modification'),
        ),
        migrations.AlterField(
            model_name='listobj',
            name='ordered',
            field=models.BooleanField(default=False, verbose_name='Ordered list (top)'),
        ),
        migrations.AlterField(
            model_name='listobj',
            name='title',
            field=models.CharField(max_length=400, verbose_name='Title'),
        ),
    ]
