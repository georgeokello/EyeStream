
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import fields
from django.http import request
from django.contrib.auth.models import User
from .models import Channels, Videos, Profile
from django.contrib import admin 


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class ChannelsForm(forms.ModelForm):
    class Meta:
        model = Channels
        fields = ['channel_name', 'description', 'facebook', 'twitter', 'google', 'channel_picture', 'channel_banner']



cat_options =(('Gaming','gaming'), ('Style','style'), ('Education','education'), ('News','news'), ('Kids','kids'), ('Entertainment','entertainment'), ('Films','films'),('Comedy','comedy'))     
class videoForm(forms.ModelForm):
    catergory = forms.ChoiceField(choices=cat_options)
    class Meta:
        model = Videos
        fields = ['video_name', 'catergory', 'video', 'about', 'channel_name', 'thumbnail']
    

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(videoForm, self).__init__(*args, **kwargs)
        self.fields['channel_name'].queryset = Channels.objects.filter(user=user)
        # self.fields['video_name'].widget = forms.TextInput(attrs={'id': 'video_name'})
        # self.fields['catergory'].widget = forms.TextInput(attrs={'id': 'catergory'})
        # self.fields['video'].widget = forms.TextInput(attrs={'id': 'video'})
        # self.fields['about'].widget = forms.TextInput(attrs={'id': 'about'})
        # self.fields['channel_name'].widget = forms.TextInput(attrs={'id': 'channel_name'})
        # self.fields['thumbnail'].widget = forms.TextInput(attrs={'id': 'thumbnail'})


class RoomFoom(forms.Form):
    room_name = forms.CharField(max_length=120,  widget= forms.TextInput
                           (attrs={
				   'id':'room-name-input'}))
