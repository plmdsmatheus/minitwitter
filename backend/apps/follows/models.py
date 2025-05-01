from django.db import models
from django.conf import settings

class Follow(models.Model):
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    ) # The user who is following
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE
    ) # The user being followed
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set the field to now when the object is first created

    class Meta:
        unique_together = ('user', 'following') # A user can only follow another user once

    def __str__(self):
        return f'{self.user.username} follows {self.following.username}'