from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Like
from .serializers import LikeSerializer

class LikeUnikeView(APIView):
    """like e unlike posts.
    If the user already liked the post, it will be unliked.
    If the user has not liked the post yet, it will be liked.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        like, created = Like.objects.get_or_create(
            user=request.user, post_id=post_id
        )
        if not created:
            return Response(
                {'detail': 'You have already liked this post.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        like = Like.objects.filter(
            user=request.user, post_id=post_id
        ).first()
        if not like:
            return Response(
                {'detail': 'You have not liked this post yet.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PostLikesListView(generics.ListAPIView):
    """List of likes for a specific post.
    This view returns a list of likes for a specific post.
    It uses the LikeSerializer to serialize the like data.
    """
    permission_classes = [permissions.AllowAny] # Permission for all users
    serializer_class = LikeSerializer 
    pagination_class = None

    def get_queryset(self):
        return Like.objects.filter(post_id=self.kwargs['post_id']) # Get likes for the specific post
