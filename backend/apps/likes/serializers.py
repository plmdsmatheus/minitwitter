from rest_framework import serializers
from .models import Like

class LikeSerializer(serializers.ModelSerializer):
    """Serializer for the Like model"""
    class Meta:
        model  = Like
        fields = ('id', 'post', 'created_at')
        read_only_fields = ('id', 'created_at')
