import sys
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.conf import settings

from .models import Post
from .serializers import PostSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow the author of a post to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for the author
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for model Post, with search, filter and ordering capabilities.
    """
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    # Filters, search and ordering
    filter_backends    = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_fields   = ['tags__name']
    search_fields      = ['text']
    ordering_fields    = ['created_at', 'like_count']
    ordering           = ['-created_at']

    def get_queryset(self):
        # queryset with annotation for like count
        qs = Post.objects.annotate(like_count=Count('likes'))
        if self.action == 'list':
            # Feed: only posts from users that the authenticated user follows
            if self.request.user.is_authenticated:
                following_ids = self.request.user.following.values_list('following_id', flat=True)
                return qs.filter(author_id__in=following_ids).select_related('author').prefetch_related('tags')
            return qs.none()
        # Retrieve, update, destroy: all posts for permissions check
        return qs.select_related('author').prefetch_related('tags')

    def list(self, request, *args, **kwargs):
        """
        List all posts with caching.

        - In test mode, no cache is applied.
        - In production, cache is applied to the list view.
        - The cache duration is set in settings.CACHE_TTL.
        """
        if 'test' in sys.argv:
            return super().list(request, *args, **kwargs)
        # Apply caching for the list view
        cached_list = cache_page(settings.CACHE_TTL)(super(PostViewSet, self).list)
        return cached_list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
