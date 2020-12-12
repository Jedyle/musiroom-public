# Generated by Django 2.1.5 on 2020-12-12 11:49

import conversations.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('read_by_all', models.DateTimeField(auto_now_add=True, verbose_name='Read by all')),
                ('unread_by', models.ManyToManyField(blank=True, related_name='unread_conversations', to=settings.AUTH_USER_MODEL, verbose_name='Unread by')),
            ],
            options={
                'verbose_name': 'Conversation',
                'verbose_name_plural': 'Conversations',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='conversations.Conversation', verbose_name='Conversation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('last_edit', models.DateTimeField(auto_now=True, verbose_name='Last edit')),
                ('text', models.TextField(max_length=4096, verbose_name='Text')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='conversation_messages', validators=[conversations.validators.FileSizeValidator(10485760)], verbose_name='Attachment')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='conversations.Conversation', verbose_name='Conversation')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'ordering': ('-date',),
            },
        ),
        migrations.AddField(
            model_name='conversation',
            name='users',
            field=models.ManyToManyField(related_name='conversations', through='conversations.Membership', to=settings.AUTH_USER_MODEL, verbose_name='Users'),
        ),
    ]
