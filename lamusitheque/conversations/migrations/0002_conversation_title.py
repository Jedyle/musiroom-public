# Generated by Django 2.1.5 on 2019-03-02 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='title',
            field=models.CharField(default='Title', max_length=100, verbose_name='Title'),
            preserve_default=False,
        ),
    ]
