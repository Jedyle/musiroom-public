# Generated by Django 2.1.5 on 2020-07-17 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import export_ratings.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('report', models.FileField(blank=True, null=True, upload_to=export_ratings.models.user_export_path, verbose_name='Rapport')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Export',
                'verbose_name_plural': 'Exports',
            },
        ),
    ]
