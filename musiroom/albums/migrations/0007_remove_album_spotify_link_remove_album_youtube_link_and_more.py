# Generated by Django 4.0.4 on 2022-05-06 14:26

from django.db import migrations, models
import django.db.models.deletion


def transfer_links_to_new_model(apps, schema_editor):
    AlbumLinks = apps.get_model("albums", "AlbumLinks")
    Album = apps.get_model("albums", "Album")
    for album in Album.objects.all():
        links = AlbumLinks(album=album)
        links.spotify = album.spotify_link
        links.youtube = album.youtube_link
        links.save()


def transfer_links_to_new_model_reverse(apps, schema_editor):
    Album = apps.get_model("albums", "Album")
    for album in Album.objects.all():
        album.spotify_link = album.links.spotify
        album.youtube_link = album.links.youtube
        album.save()


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0006_album_spotify_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumLinks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube', models.CharField(max_length=200, null=True)),
                ('spotify', models.CharField(max_length=200, null=True)),
                ('album', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='albums.album')),
            ],
        ),
        migrations.RunPython(
            transfer_links_to_new_model,
            reverse_code=transfer_links_to_new_model_reverse
        ),
        migrations.RemoveField(
            model_name='album',
            name='spotify_link',
        ),
        migrations.RemoveField(
            model_name='album',
            name='youtube_link',
        ),
    ]
