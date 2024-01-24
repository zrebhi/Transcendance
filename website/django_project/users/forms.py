from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
        def __init__(self, *args, **kwargs):
            super(CustomUserCreationForm, self).__init__(*args, **kwargs)

            # Customizing form fields
            self.fields['username'].widget = forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'maxlength': '20'  # Set maximum length for username
            })
            self.fields['username'].help_text = 'Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.'
            self.fields['password1'].widget = forms.PasswordInput(
                attrs={'class': 'form-control', 'placeholder': 'Password'})
            self.fields['password2'].widget = forms.PasswordInput(
                attrs={'class': 'form-control', 'placeholder': 'Repeat Password'})

        class Meta:
            model = User
            fields = ('username', 'password1', 'password2')

        def clean_username(self):
            username = self.cleaned_data.get('username')
            if len(username) > 20:
                raise forms.ValidationError("Username cannot be more than 20 characters.")
            return username


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)

        # Customizing form fields
        self.fields['username'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
