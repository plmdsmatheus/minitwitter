from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_follow_notification(follower_id, followed_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    follower = User.objects.get(pk=follower_id)
    followed = User.objects.get(pk=followed_id)

    subject = f'New follower: {follower.username}'
    message = (
        f'Hello {followed.username},\n\n'
        f'{follower.username} start follow you on MiniTwitter .\n\n'
        'Enjoy the app,\nMiniTwitter Team'
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [followed.email],
        fail_silently=False,
    )
