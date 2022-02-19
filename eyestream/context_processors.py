from .models import Channels

def get_notification(request):

    notification_count = 0
    data = {
        "notification_count":notification_count
    }
    return data