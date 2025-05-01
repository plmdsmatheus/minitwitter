from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts') # The user who created the post
    text = models.TextField(max_length=280) # Max length of a tweet
    image = models.ImageField(upload_to='posts/', blank=True, null=True) # Optional
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set the field to now when the object is first created
    tags = TaggableManager(blank=True) # Optional, for tagging posts

    class Meta:
        ordering = ['-created_at'] # Newest posts first

    def __str__(self):
        return f'{self.author.username}: {self.text[:20]}' # Limit to 20 characters