from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from app.models import User


class UserCForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput,required=False)
    password2 = forms.CharField(label='Password', widget=forms.PasswordInput,required=False)
    class Meta:
        model = User
        fields = ('chat_id',)



class UserMForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'chat_id', 'password')
