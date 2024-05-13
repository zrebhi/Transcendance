from django import forms
from .models import Tournament


class TournamentCreationForm(forms.ModelForm):

    size = forms.ChoiceField( 
        choices=[(4, '4'), (8, '8')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Tournament
        fields = ['name', 'size']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Default placeholder'}),
        }

    def __init__(self, *args, **kwargs):
        creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)
        if creator:
            # This will set the placeholder to the creator's username if a creator is provided
            self.fields['name'].widget.attrs['placeholder'] = f"{creator}'s tournament"

from django import forms

class TournamentNicknameForm(forms.Form):
    tournament_nickname = forms.CharField(
        label='Choose a nickname for the tournament',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'max_length': 'Nickname cannot be more than 20 characters.'
        }
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pop user from kwargs to avoid affecting superclass initialization
        super(TournamentNicknameForm, self).__init__(*args, **kwargs)
        
        # Set the placeholder to the user's username if a user object is provided
        if user:
            self.fields['tournament_nickname'].widget.attrs['placeholder'] = f"{user.username}"
