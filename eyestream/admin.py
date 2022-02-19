from django.contrib import admin

from .models import Channels, Videos, VideoViews, Profile

admin.site.register(Profile)
admin.site.register(Channels)
admin.site.register(Videos)
admin.site.register(VideoViews)