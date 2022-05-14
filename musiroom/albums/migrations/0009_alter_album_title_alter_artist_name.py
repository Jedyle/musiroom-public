# Generated by Django 4.0.4 on 2022-05-14 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0008_albumlinks_deezer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='title',
            field=models.CharField(db_index=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='artist',
            name='name',
            field=models.CharField(db_index=True, max_length=100),
        ),
    ]
