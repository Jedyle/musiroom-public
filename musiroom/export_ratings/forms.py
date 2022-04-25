from django import forms


class SCExportForm(forms.Form):
    sc_url = forms.CharField(label="Url Senscritique",
                             help_text="Saisissez l'url de votre profil Senscritique. "
                                       "ATTENTION : l'export ne fonctionnera que si votre "
                                       "profil et vos notes sont publics et visibles par tous.")
    erase = forms.BooleanField(label="Remplacer mes notes en cas de conflit", required=False,
                               help_text="Si vous cochez cette case, les notes "
                                         "des albums que vous avez déja notés sur "
                                         "le site seront remplacées en cas de conflit, "
                                         "sinon elles seront conservées.")

    FIELDS = (
        ('LP', 'Albums'),
        ('EP', 'EPs'),
        ('Live', 'Live'),
        ('Compilation', 'Compilations'),
        ('OST', 'Bandes Originales'),
        ('Single', 'Singles')
    )

    fields = forms.MultipleChoiceField(label="Types a exporter", widget=forms.CheckboxSelectMultiple, choices=FIELDS,
                                       help_text="Les autres catégories (comme Mixtape ou Remix) "
                                                 "ne sont pas prises en compte")
