from django.urls import path
from .views import LikeUnikeView, PostLikesListView

urlpatterns = [
    path('like/<int:post_id>/', LikeUnikeView.as_view(),     name='post-like'), # Like or unlike a post
    path('unlike/<int:post_id>/', LikeUnikeView.as_view(),     name='post-unlike'), # Like or unlike a post
    path('post/<int:post_id>/', PostLikesListView.as_view(), name='post-likes-list'), # List of users who liked a specific post
]
