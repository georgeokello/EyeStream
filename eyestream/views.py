from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from . forms import UserRegisterForm, UserUpdateForm, ChannelsForm, videoForm, ProfileUpdateForm, RoomFoom
from django.contrib.auth.decorators import login_required
from . models import Channels, Videos, VideoViews, Profile
from django.db.models import Count
from django.http import HttpResponse
from moviepy.editor import *



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

def joinARoomBtn(request):
    return render(request, 'joinARoomBtn.html')

def Home(request):
    videos = Videos.objects.all()
    channels = Channels.objects.all()
    return render(request,'index.html', {'videos':videos, 'channels':channels})



def channels(request):
    videos = Videos.objects.all()
    channels = Channels.objects.all()
    return render(request, 'channels.html', {'videos':videos, 'channels':channels})



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
            
            data={
            'error': False, 
            'message': 'Uploaded Successfully'
            }
            return JsonResponse(data, safe=False)
            # messages.success(request, f'Your account has been updated!')
            # return redirect('Home')

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
        form = videoForm(request.user,request.POST, request.FILES,)
        if form.is_valid():
            obj = form.save(commit=False)
            vid = request.FILES['id_video'][0]
            clip = VideoFileClip(vid.temporary_file_path())
            obj.duration = clip.duration
            print()
            obj.save(clip.duration)
            data={
            'error': False, 
            'message': 'Uploaded Successfully'
            }
            return JsonResponse(data, safe=False)
        else:
                return JsonResponse({'error': True, 'errors': 'Error occured'})
    else:
        form = videoForm(request.user)
    return render(request, 'upload.html', {'form': form})


@login_required(login_url=("login"))
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

@login_required(login_url=("login"))
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


# video chat

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
from twilio.jwt.access_token.grants import VideoGrant
import string
import random


# Load environment variables from a .env file
load_dotenv()

# Create a Twilio client
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
api_key = os.environ["TWILIO_API_KEY_SID"]
api_secret = os.environ["TWILIO_API_KEY_SECRET"]
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = twilio.rest.Client(api_key, api_secret, account_sid)


def find_or_create_room(room_name):
    try:
        # try to fetch an in-progress room with this name
        twilio_client.video.rooms(room_name).fetch()
    except twilio.base.exceptions.TwilioRestException:
        # the room did not exist, so create it
        twilio_client.video.rooms.create(unique_name=room_name, type="group")


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


# # livestream
# twilio_live_account_sid = os.environ['TWILIO_LIVE_ACCOUNT_SID']
# api_live_key = os.environ["TWILIO_LIVE_API_KEY_SID"]
# api_live_secret = os.environ["TWILIO_LIVE_API_KEY_SECRET"]
# auth_live_token = os.environ['TWILIO_LIVE_AUTH_TOKEN']


# client = Client(api_live_key, api_live_secret, twilio_live_account_sid)

# def streamer(request):
#     return render(request, 'streamerPage.html')

# def audience(request):
#     return render(request, 'audience.html')

# def playStreamer():
#     player_streamer = client.media.player_streamer.create()
#     return player_streamer.sid


# def create_room(room_name):
#     try:
#         # create the room
#         client.video.rooms.create(unique_name=room_name, type="go")
#     except twilio.base.exceptions.TwilioRestException:
#         print('coulfnt create the room')
    

# def startStream(request):
#     room = ''
#     # room name
#     data = json.loads(request.body)
#         # extract the room_name from the JSON body of the POST request
#     room_name = data['streamName']
#         # find an existing room with this room_name, or create one

#     # Create the WebRTC Go video room,
    
#     create_room(room_name)
    
#     # fetch the created room
#     room = client.video.rooms(room_name).fetch()
    

#     player_streamer1 = client.media.player_streamer.list(limit=20)

#     for record in player_streamer1:
#         print(record.sid)
#         client.media \
#             .player_streamer(record.sid) \
#             .update(status='ended')
#         print(record.sid)

#     # Create PlayerStreamer
#     player_streamer = client.media.player_streamer.create()
    
#     # Create the WebRTC Go video room, PlayerStreamer, and MediaProcessors
#     media_processor = client.media \
#         .media_processor \
#         .create(
#             extension='video-composer-v1',
#             extension_context=json.dumps({
#                 'identity': 'video-composer-v1',
#                 'room': {
#                     'name': room.sid
#                 },
#                 'outputs': [
#                     player_streamer.sid
#                 ]
#             })
#         )

#     data = {
#         'roomId': room.sid,
#         'streamName': room_name,
#         'playerStreamerId': player_streamer.sid,
#         'mediaProcessorId': media_processor.sid
#     } 
#     return JsonResponse(data, safe=False)       



# def endLiveStream(request):
#      # stream details
#     data = json.loads(request.body)
#         # extract the room_name from the JSON body of the POST request
#     stream_details = data['streamDetails']
#         # find an existing room with this room_name, or create one

#     # End the player streamer, media processor, and video room
#     streamName  = stream_details.streamName
#     roomId  = stream_details.roomId
#     playerStreamerId = stream_details.playerStreamerId
#     mediaProcessorId = stream_details.mediaProcessorId

#     client.media \
#         .media_processor(mediaProcessorId) \
#         .update(status='ended')

#     client.media \
#         .player_streamer(playerStreamerId) \
#         .update(status='ended')
    
#     client.video.rooms(roomId) \
#         .update(status='completed')

#     return f"successfully ended {streamName} room"


# def streamerToken(request):
#     # room name 
#     data = json.loads(request.body)
#         # extract the room_name from the JSON body of the POST request
#     room_name = data['room']
#     identity = data['identity']
#         # find an existing room with this room_name, or create one

#     token = AccessToken(twilio_live_account_sid, api_live_key, api_live_secret)
#     video_grant = VideoGrant(room=room_name)
#     token.add_grant(video_grant)
#     token.identity = identity
#     data = {"token": token.to_jwt()}
#     return JsonResponse(data, safe=False)


# def audienceToken(request):
#     # generate random string for the client identity
#     number_of_character = 20
#     # call random.choice to find the string in uppercase + numeric data
#     randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=number_of_character))
#     identity = str(randomString)

#     #Get the first player streamer
#     playerStreamerList = client.media.player_streamer.list(status='started', limit=20)
#     playStreamer = True if len()
#     if(len(playerStreamerList) == 0):
#         mgs = "No one is streaming"
#         return HttpResponse(mgs)

#     # Otherwise create an access token with a PlaybackGrant for the livestream
#     token = AccessToken(twilio_live_account_sid, api_live_key, api_live_secret)

#     # Create a playback grant and attach it to the access token
#     playback_grant = client.media \
#         .player_streamer(playStreamer()) \
#         .playback_grant() \
#         .create()

#     # wrap grant and attach to the token
#     wrapped_grant = PlaybackGrant(grant=playback_grant.grant)
#     token.add_grant(wrapped_grant)
#     token.identity = identity
#     data = {"token": token.to_jwt()}
#     return JsonResponse(data, safe=False)
        



