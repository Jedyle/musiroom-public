# Generated by Django 2.1.5 on 2019-03-02 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0002_conversation_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='archived_by',
        ),
    ]
