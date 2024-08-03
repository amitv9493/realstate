from django import forms


class RedirectForm(forms.Form):
    password = forms.CharField(
        label="Password",
        max_length=100,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        max_length=100,
        widget=forms.PasswordInput,
    )
