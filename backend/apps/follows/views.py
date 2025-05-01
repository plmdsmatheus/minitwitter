from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Follow
from .serializers import FollowSerializer, UserSerializer

User = get_user_model()

class FollowUnfollowView(APIView):
    """Follow or unfollow a user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response(
                {'detail': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        target = generics.get_object_or_404(User, pk=user_id)
        follow, created = Follow.objects.get_or_create(
            user=request.user,
            following=target
        )
        if not created:
            return Response(
                {'detail': 'You are already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        follow = Follow.objects.filter(
            user=request.user,
            following__id=user_id
        ).first()
        if not follow:
            return Response(
                {'detail': 'You are not following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FollowersListView(generics.ListAPIView):
    """List of users following the authenticated user."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class  = UserSerializer
    pagination_class  = None

    def get_queryset(self):
        return User.objects.filter(
            following__following=self.request.user
        )

class FollowingListView(generics.ListAPIView):
    """List of users the authenticated user is following."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class  = UserSerializer
    pagination_class  = None

    def get_queryset(self):
        return User.objects.filter(
            followers__user=self.request.user
        )
