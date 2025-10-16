from django import forms
from django.contrib.auth.models import User

from .models import Profile, User

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
    
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="parol",
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label="parolni tasdiqlang",
                                widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
        
    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError("Parollar mos emas")
        return data['password2']
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']