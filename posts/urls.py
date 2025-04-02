from django.urls import path
from .views import (
    UserListCreate, UserDetailView,
    PostView,
    CommentListCreateView, CommentDetailView,
    PostLikeListCreateView, PostLikeDetailView,
    CommentLikeListCreateView, CommentLikeDetailView, FollowView, UnfollowView, UserFollowView, NewsFeedView,
)

urlpatterns = [
    # User endpoints
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/follow-info/', UserFollowView.as_view(), name='user-follow-info'),

    # Post endpoints
    path('posts/', PostView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostView.as_view(), name='post-detail'),

    # Comment endpoints
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    # PostLike endpoints
    path('post-likes/', PostLikeListCreateView.as_view(), name='post-like-list-create'),
    path('post-likes/<int:pk>/', PostLikeDetailView.as_view(), name='post-like-detail'),

    # CommentLike endpoints
    path('comment-likes/', CommentLikeListCreateView.as_view(), name='comment-like-list-create'),
    path('comment-likes/<int:pk>/', CommentLikeDetailView.as_view(), name='comment-like-detail'),

    # Follow/Unfollow endpoints
    path('follow/<int:followed_user_id>/', FollowView.as_view(), name='follow-user'),
    path('unfollow/<int:followed_user_id>/', UnfollowView.as_view(), name='unfollow-user'),

    # Feed Endpoints
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    
]
