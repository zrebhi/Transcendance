from django import forms
from .models import Tournament


class TournamentCreationForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['max_players']  # List the fields you want in the form
        widgets = {
            'max_players': forms.NumberInput(attrs={'class': 'form-control',
                                                    'placeholder': 'Maximum Number of Players (4 to 8)'}),
        }
        labels = {
            'max_players': 'Maximum Number of Players (4 to 8)',
        }

    def clean_max_players(self):
        max_players = self.cleaned_data.get('max_players')
        if not 4 <= max_players <= 8:
            raise forms.ValidationError("Invalid number of players. Choose a number between 4 and 8.")
        return max_players
