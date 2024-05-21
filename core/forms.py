from django import forms
from django.contrib.auth import get_user_model


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = {
            "first_name",
            "last_name",
            "username",
            "email",
        }
        widgets = {
            "first_name": forms.widgets.TextInput(attrs={"class": "form-control mb-3"}),
            "last_name": forms.widgets.TextInput(attrs={"class": "form-control mb-3"}),
            "username": forms.widgets.TextInput(attrs={"class": "form-control mb-3"}),
            "email": forms.widgets.EmailInput(attrs={"class": "form-control mb-3"}),
        }

    def clean_check_password(self):
        if self.cleaned_data["password"] != self.cleaned_data["confirm_password"]:
            raise forms.ValidationError("The Passwords are not the same")
        return self.cleaned_data["confirm_password"]

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=True)
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class AuthorizationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = {
            "username",
            "password",
        }
        widgets = {
            'username': forms.widgets.TextInput(attrs={"class": "form-control mb-3"}),
            'password': forms.widgets.TextInput(attrs={"class": "form-control mb-3"}),
        }
