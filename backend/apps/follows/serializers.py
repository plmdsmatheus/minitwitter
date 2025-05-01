from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()

class FollowSerializer(serializers.ModelSerializer):
    """Serializer for the Follow model"""
    class Meta:
        model = Follow
        fields = ('id', 'following', 'created_at')
        read_only_fields = ('id', 'created_at')

class UserSerializer(serializers.ModelSerializer):
    """Serializer for listing users are followed or following the user """
    follower_count = serializers.SerializerMethodField() # Custom field to count followers
    following_count = serializers.SerializerMethodField() # Custom field to count following

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'follower_count', 'following_count')

    def get_follower_count(self, obj):
        """
        Custom method to count the number of followers for a user.
        This method is used to calculate the number of followers for a user.
        """
        return obj.followers.count()
    def get_following_count(self, obj):
        """
        Custom method to count the number of users a user is following.
        This method is used to calculate the number of users a user is following.
        """
        return obj.following.count()