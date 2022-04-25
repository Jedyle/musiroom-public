from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import Discussion


class DiscussionForm(forms.Form):
    title = forms.CharField(label='Titre', max_length=200)
    content = forms.CharField(label='Contenu', widget=forms.Textarea(attrs={'rows': 18}))

    def __init__(self, target_object=None, *args, **kwargs):
        super(DiscussionForm, self).__init__(*args, **kwargs)
        self.target_object = target_object

    def get_discussion_object(self):
        """
        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.
        """
        if not self.is_valid():
            raise ValueError("get_discussion_object may only be called on valid forms")

        new = Discussion(**self.get_discussion_create_data())
        return new

    def get_discussion_create_data(self):
        """
        Returns the dict of data to be used to create a discussion.
        """
        if self.target_object is not None:
            return dict(
                content_type=ContentType.objects.get_for_model(self.target_object),
                object_id=self.target_object.pk,
                title=self.cleaned_data['title'],
                content=self.cleaned_data['content'],
            )
        else:
            return dict(
                title=self.cleaned_data['title'],
                content=self.cleaned_data['content'],
            )


class EditDiscussionForm(forms.ModelForm):
    title = forms.CharField(label="Titre", max_length=200, required=True)
    content = forms.CharField(label='Contenu', required=True, widget=forms.Textarea(attrs={'rows': 18}))

    class Meta:
        model = Discussion
        fields = ['title', 'content']
