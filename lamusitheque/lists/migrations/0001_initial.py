# Generated by Django 2.1.5 on 2019-02-17 21:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('albums', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ListItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, max_length=500)),
                ('order', models.IntegerField(default=-1)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='albums.Album')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ListObj',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_score', models.IntegerField(db_index=True, default=0)),
                ('num_vote_up', models.PositiveIntegerField(db_index=True, default=0)),
                ('num_vote_down', models.PositiveIntegerField(db_index=True, default=0)),
                ('title', models.CharField(max_length=400, verbose_name='Titre')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('ordered', models.BooleanField(default=False, verbose_name='Liste ordonnée (top)')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
                ('albums', models.ManyToManyField(related_name='lists', through='lists.ListItem', to='albums.Album')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'liste',
                'verbose_name_plural': 'listes',
                'ordering': ['-vote_score'],
            },
        ),
        migrations.AddField(
            model_name='listitem',
            name='item_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lists.ListObj'),
        ),
    ]
