# Generated by Django 2.1.5 on 2020-07-17 16:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import moderation.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModeratedObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_pk', models.PositiveIntegerField(blank=True, editable=False, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('state', models.SmallIntegerField(choices=[(0, 'Ready for moderation'), (1, 'Draft')], default=1, editable=False)),
                ('status', models.SmallIntegerField(choices=[(0, 'Rejected'), (1, 'Approved'), (2, 'Pending')], default=2, editable=False)),
                ('on', models.DateTimeField(blank=True, editable=False, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('changed_object', moderation.fields.SerializedObjectField(editable=False)),
                ('by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moderated_objects', to=settings.AUTH_USER_MODEL)),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='changed_by_set', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Objet à modérer',
                'verbose_name_plural': 'Objets à modérer',
                'ordering': ['status', 'created'],
            },
        ),
    ]
