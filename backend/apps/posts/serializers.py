from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    like_count = serializers.SerializerMethodField() # Custom field to count likes
    tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    tag_list   = serializers.ListField(
        source='tags.names',
        read_only=True
    )

    class Meta:
        model  = Post
        fields = ('id', 'author', 'text', 'image', 'created_at', 'like_count', 'tags', 'tag_list')
        read_only_fields = ('id', 'author', 'created_at', 'like_count', 'tag_list')

    def get_like_count(self, obj):
        """
        Custom method to count the number of likes for a post.
        This method is used to calculate the number of likes for a post.
        """
        return obj.likes.count()

    def create(self, validated_data):
        # exctract the tags and author from the validated data
        tags   = validated_data.pop('tags', [])
        author = validated_data.pop('author')
        post = Post.objects.create(author=author, **validated_data)
        if tags:
            post.tags.set(tags)
        return post