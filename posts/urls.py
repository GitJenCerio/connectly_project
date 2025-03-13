from django.urls import path
from .views import UserListCreate, PostListCreate, CommentListCreate, UserLogin

urlpatterns = [
    # Class-based views (CBVs)
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
]
