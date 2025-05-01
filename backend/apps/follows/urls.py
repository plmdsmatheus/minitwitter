from django.urls import path
from .views import (
    FollowUnfollowView,
    FollowersListView,
    FollowingListView,
)

urlpatterns = [
    path('follow/<int:user_id>/', FollowUnfollowView.as_view(), name='follow'), # Follow a user
    path('unfollow/<int:user_id>/', FollowUnfollowView.as_view(), name='unfollow'), # Unfollow a user
    path('followers/', FollowersListView.as_view(), name='followers-list'), # List of users following the authenticated user
    path('following/', FollowingListView.as_view(), name='following-list'), # List of users the authenticated user is following
]
