# Generated by Django 2.1.5 on 2019-03-02 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0003_remove_conversation_archived_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='notified',
        ),
        migrations.AddField(
            model_name='message',
            name='last_edit',
            field=models.DateTimeField(auto_now=True, verbose_name='Last edit'),
        ),
    ]