from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.files.storage import default_storage as storage



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg',null=True, blank=True, upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
   

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        # img = Image.open(self.image.name)
        img = Image.open(storage.open(self.image.name))
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.name)

       


@receiver(post_save, sender=User)
def create_profile(sender, created, instance, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Channels(models.Model):
    channel_name = models.CharField(max_length=120)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='channel_user')
    description = models.TextField()
    subscribers = models.ManyToManyField(User, related_name='subscribers_count')
    facebook = models.CharField(max_length=120,null=True)
    twitter = models.CharField(max_length=120, null=True)
    google = models.CharField(max_length=120, null=True)
    channel_picture = models.ImageField(default="default.jpg", null=True, blank=True, upload_to='channel_pics')
    channel_banner = models.ImageField( default="default.jpg", null=True, blank=True, upload_to='channel_banner_pics')

    def __str__(self):
        return f"{self.channel_name}"


class Videos(models.Model):
    video_name = models.CharField(max_length=120)
    catergory = models.CharField(max_length=120)
    video = models.FileField(upload_to='uploaded_videos')
    about = models.TextField(max_length=120)
    channel_name = models.ForeignKey(Channels, on_delete=models.CASCADE, related_name='video_channel')
    thumbnail = models.ImageField(default="default.jpg", null=True, blank=True, upload_to='video_thumbnail')
    date = models.DateField(auto_now=True)

    # existingPath = models.CharField(unique=True, max_length=100)
    # eof = models.BooleanField()

    def __str__(self):
        return f"channel - {self.channel_name} -- {self.video_name}"
        

class VideoViews(models.Model):
    video = models.ForeignKey(Videos, on_delete=models.CASCADE, related_name='view_count')
    ip_addr = models.CharField(max_length=120)
    session = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.ip_addr}"