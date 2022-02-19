from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from . forms import UserRegisterForm, UserUpdateForm, ChannelsForm, videoForm, ProfileUpdateForm, RoomFoom
from django.contrib.auth.decorators import login_required
from . models import Channels, Videos, VideoViews, Profile



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'forms': form})



def Home(request):
    videos = Videos.objects.all()
    channels = Channels.objects.all()

    return render(request,'index.html', {'videos':videos, 'channels':channels})



def channels(request):
    videos = Videos.objects.all()
    channels = Channels.objects.all()
    return render(request, 'channels.html', {'videos':videos,'channels':channels})



def forgot_password(request):
    return render(request,'registration/forgot_password.html')


@login_required(login_url=("login"))
def create_channel(request):
    if request.method == 'POST':
        c_form = ChannelsForm(request.POST, request.FILES)
        if c_form.is_valid():
            channel_name = c_form.cleaned_data['channel_name']
            description = c_form.cleaned_data['description']
            facebook = c_form.cleaned_data['facebook']
            twitter = c_form.cleaned_data['twitter']
            google = c_form.cleaned_data['google']
            channel_picture = c_form.cleaned_data['channel_picture']
            channel_banner = c_form.cleaned_data['channel_banner']

            Channels.objects.create(
                channel_name = channel_name,
                user = request.user,
                description = description,
                # subscribers = subscribers.set()
                facebook = facebook,
                twitter = twitter,
                google = google,
                channel_picture = channel_picture,
                channel_banner = channel_banner
            )
            return redirect('channels')
    else:
        c_form = ChannelsForm()
    return render(request, 'create_channel.html', {'c_form': c_form})



def channel_details(request, pk):
    channel = get_object_or_404(Channels, pk=pk)
    channel_name = channel.id
    videos = Videos.objects.filter(channel_name=channel_name)
    subscribers = channel.subscribers.count()
    pk = pk
    return render(request, 'channel_details.html', {'channel':channel, 'videos':videos, 'subscribers':subscribers})



@login_required(login_url=("login"))
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('UserProfile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile.html', context)
    

@login_required(login_url=("login"))
def upload(request):

    if request.method == 'POST':
        v_form = videoForm(request.user,request.POST, request.FILES,)
        if v_form.is_valid():
            v_form.save()
            return redirect('channels')
    else:
        v_form = videoForm(request.user)
    return render(request, 'upload.html', {'v_form': v_form})


def play_video(request, pk):
    video = get_object_or_404(Videos, pk=pk)
    videos = Videos.objects.filter(catergory=video.catergory).exclude(video=video.video)
    pk = pk
    
    ip = request.META['REMOTE_ADDR']
    if not VideoViews.objects.filter(video=video, session=request.session.session_key):
        view = VideoViews(video=video, ip_addr=ip, session=request.session.session_key)
        view.save()
    video_views = VideoViews.objects.filter(video=video).count()
    subscribers_count = video.channel_name.subscribers.count()
    context = {
        'video':video, 
        'videos':videos, 
        'video_views':video_views,
        'subscribers_count':subscribers_count,
        }

    return render(request, 'video-page.html', context)


def subscribe_btn(request):
    subscriber = request.user
    subscribed = False
    if request.method == "POST":
        channel_id = request.POST['channel-id']
        channel = get_object_or_404(Channels, id=channel_id)
        if subscriber in channel.subscribers.all():
            channel.subscribers.remove(subscriber)
            subscribed = False
        else:
            channel.subscribers.add(subscriber)
            subscribed=True
        data={
            'subscibed': subscribed,
            'num_subscribers': channel.subscribers.count()
        }
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'error ocured'})

def searchVideo(request):
    if request.method == "POST":
        search_value = request.POST['search_value']
        videos = Videos.objects.filter(video_name__contains=search_value)
        return render(request, "search.html", {'videos':videos, 'search': search_value})
    else:
        return render(request, "search.html")


# streaming 

import os
import uuid  # for generating random user id values

import twilio.jwt.access_token
import twilio.jwt.access_token.grants
import twilio.rest

# for livestream
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import PlaybackGrant
from dotenv import load_dotenv
from twilio.rest import Client
import json


# Load environment variables from a .env file
load_dotenv()

# Create a Twilio client
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY_SID"]
api_secret = os.environ["TWILIO_API_KEY_SECRET"]
twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)


def find_or_create_room(room_name):
    try:
        # try to fetch an in-progress room with this name
        twilio_client.video.rooms(room_name).fetch()
    except twilio.base.exceptions.TwilioRestException:
        # the room did not exist, so create it
        twilio_client.video.rooms.create(unique_name=room_name, type="go")


def get_access_token(room_name):
    # create the access token
    access_token = twilio.jwt.access_token.AccessToken(
        account_sid, api_key, api_secret, identity=uuid.uuid4().int
    )
    # create the video grant
    video_grant = twilio.jwt.access_token.grants.VideoGrant(room=room_name)
    # Add the video grant to the access token
    access_token.add_grant(video_grant)
    return access_token


def Live(request):     
    return render(request, 'live.html')


def join_room(request):
    data = json.loads(request.body)
        # extract the room_name from the JSON body of the POST request
    room_name = data['room_name']
        # find an existing room with this room_name, or create one
    find_or_create_room(room_name)
        # retrieve an access token for this room
    access_token = get_access_token(room_name)
        # return the decoded access token in the response
        # NOTE: if you are using version 6 of the Python Twilio Helper Library,
        # you should call `access_token.to_jwt().decode()`
    data = {"token": access_token.to_jwt()}
    return JsonResponse(data, safe=False)
