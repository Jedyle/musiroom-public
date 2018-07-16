from django import forms
from .models import Genre, AlbumGenre
from .fields import ListTextWidget

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description', 'slug', 'parent']


class AlbumGenreForm(forms.Form):
    genre_list = forms.CharField(required = True,
                                 label= 'Ajouter un genre',
                                 help_text = 'Le genre ajouté sera votable par tous les utilisateurs. Tout abus (comme ajouter Death Metal pour Britney Spears) sera sanctionné')

    def __init__(self, *args, **kwargs):
        _genre_list = kwargs.pop('data_list', None)
        super(AlbumGenreForm, self).__init__(*args, **kwargs)
        self.fields['genre_list'].widget = ListTextWidget(data_list=_genre_list, name='genre-list')

