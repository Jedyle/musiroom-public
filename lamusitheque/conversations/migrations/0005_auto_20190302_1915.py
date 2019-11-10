# Generated by Django 2.1.5 on 2019-03-02 18:15

import conversations.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0004_auto_20190302_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='conversation_messages', validators=[conversations.validators.FileSizeValidator(10485760)], verbose_name='Attachment'),
        ),
    ]