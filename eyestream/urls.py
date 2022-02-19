
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', views.register, name='register'),
    path('', views.Home, name='Home'),
    path('logout', LogoutView.as_view(next_page='login'), name='logout'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('profile/', views.profile, name='UserProfile'),
    path('logout', LogoutView.as_view(next_page='login'), name='logout'),
    path('channels', views.channels, name='channels'),
    path('create_channel', views.create_channel, name='create_channel' ),
    path('channel_details/<int:pk>', views.channel_details, name='channel_details'),
    path('upload', views.upload, name='upload'),
    path('subscribe', views.subscribe_btn, name='subscribe'),
    path('play_video/<int:pk>', views.play_video, name='play_video'),
    path('live', views.Live, name='live'),
    path('join_room', views.join_room, name='join_room'),
    path('search', views.searchVideo, name='search'),
]