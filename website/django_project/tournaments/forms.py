from django import forms
from .models import Tournament


class TournamentCreationForm(forms.ModelForm):

    class Meta:
        model = Tournament
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Default placeholder'}),
        }

    def __init__(self, *args, **kwargs):
        creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)
        if creator:
            # This will set the placeholder to the creator's alias if a creator is provided
            self.fields['name'].widget.attrs['placeholder'] = f"{creator}'s tournament"
