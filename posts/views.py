# posts/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from .models import Post, Comment, PostLike, CommentLike, Follow
from .serializers import (
    UserSerializer, PostSerializer, CommentSerializer,
    PostLikeSerializer, CommentLikeSerializer
)
from factories.post_factory import PostFactory
from django.contrib.auth.models import User
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from factories.feed_factory import FeedFactory
from .permissions import IsAuthorOrReadOnly, IsAuthorOrAdmin
from .utils import has_role
from .base import BaseLoggedAPIView
from hashlib import md5
from rest_framework.permissions import AllowAny




# -----------------------------
#   USER VIEWS
# -----------------------------
from singletons.logger_singleton import LoggerSingleton


logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")



class UserListCreate(BaseLoggedAPIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(BaseLoggedAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrReadOnly]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            self.logger.info(f"Updated user: {updated_user.username}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user and not has_role(request.user, 'admin'):
            return Response({"error": "You do not have permission to delete this user."}, status=status.HTTP_403_FORBIDDEN)
        username = user.username
        self.logger.info(f"Deleted user: {username}")
        user.delete()
        return Response({"message": f"User '{username}' has been deleted successfully.", "user_id": pk}, status=status.HTTP_200_OK)
# -----------------------------
#   POST VIEWS
# -----------------------------
class PostView(BaseLoggedAPIView):
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        elif self.request.method == 'PUT':
            return [IsAuthorOrReadOnly()]
        elif self.request.method == 'DELETE':
            return [IsAuthorOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk=None):
        user = request.user if request.user.is_authenticated else None

        if pk:
            post = self.get_object(pk)
            if post.privacy == 'private':
                if not user or post.author != user:
                    return Response({'detail': 'This post is private.'}, status=status.HTTP_403_FORBIDDEN)
            serializer = PostSerializer(post)
            return Response(serializer.data)

        # List view: return public posts for guests; public + own private posts for authenticated users
        if user:
            posts = Post.objects.filter(Q(privacy='public') | Q(author=user))
        else:
            posts = Post.objects.filter(privacy='public')

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


    def post(self, request):
        if has_role(request.user, 'guest'):
            return Response({'error': 'Guests are not allowed to create posts.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                privacy=data.get('privacy', 'public'),  # 👈 include this!
                author=request.user
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        
        except KeyError as e:
            return Response({'error': f'Missing field: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk=None):
        if not pk:
            return Response({'error': 'Post ID is required for PUT'}, status=status.HTTP_400_BAD_REQUEST)
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            updated_post = serializer.save()
            self.logger.info(f"Updated post: {updated_post.title}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': 'Post ID is required for DELETE'}, status=status.HTTP_400_BAD_REQUEST)
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        self.logger.info(f"Deleted post: {post.title}")
        post.delete()
        return Response({"message": f"Post '{post.title}' has been deleted successfully.", "post_id": pk}, status=status.HTTP_200_OK)

# -----------------------------
#   COMMENT VIEWS
# -----------------------------

class CommentListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        if has_role(request.user, 'guest'):
            return Response({'error': 'Guests cannot comment.'}, status=status.HTTP_403_FORBIDDEN)
        # Pass request in the context so that the serializer can auto-assign the author
        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()
            logger.info(f"Created comment #{comment.id} by {comment.author.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Error creating comment: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get(self, request, pk):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_comment = serializer.save()
            logger.info(f"Updated comment #{updated_comment.id}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment)
        logger.info(f"Deleted comment #{comment.id}")
        comment.delete()
        return Response({"message": f"Comment #{comment.id} has been deleted successfully."
        }, status=status.HTTP_200_OK)


# -----------------------------
#   POST LIKE VIEWS
# -----------------------------


class PostLikeDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(PostLike, pk=pk)

    def get(self, request, pk):
        post_like = self.get_object(pk)
        serializer = PostLikeSerializer(post_like, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk):
        post_like = self.get_object(pk)

        # Allow only the user who created the like to delete it
        if request.user != post_like.user:
            return Response(
                {"error": "You are not allowed to remove this like."},
                status=status.HTTP_403_FORBIDDEN
            )

        logger.info(f"Removing like from {post_like.user.username} on {post_like.post.title}")
        post_like.delete()

        return Response({
            "message": f"{post_like.user.username} unliked post '{post_like.post.title}' successfully."
        }, status=status.HTTP_200_OK)


# -----------------------------
#   COMMENT LIKE VIEWS
# -----------------------------
class CommentLikeListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        comment_likes = CommentLike.objects.all()
        serializer = CommentLikeSerializer(comment_likes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentLikeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comment_like = serializer.save()
            logger.info(f"{comment_like.user.username} liked comment #{comment_like.comment.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Error creating comment like: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentLikeDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(CommentLike, pk=pk)

    def get(self, request, pk):
        comment_like = self.get_object(pk)
        serializer = CommentLikeSerializer(comment_like, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk):
        comment_like = self.get_object(pk)
        logger.info(f"Removing like from {comment_like.user.username} on comment #{comment_like.comment.id}")
        return Response({
            "message": f"{comment_like.user.username} unliked comment #{comment_like.comment.id} successfully."
        }, status=status.HTTP_200_OK)

    

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        return Response({"message": "Authenticated!"})

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def get_response_data(self, serializer):
        """
        Customize the response data to include user details.
        """
        data = super().get_response_data(serializer)
        # Check if the user has a profile picture URL (optional, if implemented)
        user = self.user
        extra = {
            "pk": user.pk,
            "email": user.email,
            "username": user.username,
        }
        # If you are storing a profile picture URL, include it
        if hasattr(user, "profile") and user.profile.image_url:
            extra["profile_picture"] = user.profile.image_url
        data["user"] = extra
        return data

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error("Google OAuth login failed: %s", str(e))
            return Response(
                {"error": "Google login failed. " + str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class FeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class NewsFeedView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Handle unauthenticated users
        user = request.user if request.user.is_authenticated else None
        filter_param = request.query_params.get('filter')
        page_number = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        # Safe cache key even for anonymous users
        user_id = user.id if user else 'anon'
        key_raw = f"feed:{user_id}:{filter_param}:{page_number}:{page_size}"
        cache_key = md5(key_raw.encode()).hexdigest()

        # Check cache
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # Get feed
        feed = FeedFactory(user).get_feed(filter_param)

        # Paginate
        paginator = FeedPagination()
        result_page = paginator.paginate_queryset(feed, request)
        serializer = PostSerializer(result_page, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)

        # Cache paginated data
        cache.set(cache_key, paginated_response.data, timeout=60)
        return paginated_response
    
import logging
logger = logging.getLogger(__name__)

class PostLikeListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    

    def get(self, request):
        post_likes = PostLike.objects.all()
        serializer = PostLikeSerializer(post_likes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostLikeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post_like = serializer.save()
            logger.info(f"{post_like.user.username} liked {post_like.post.title}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Error creating post like: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request, followed_user_id):
        if has_role(request.user, 'guest'):
            return Response({'error': 'Guests cannot follow or unfollow users.'}, status=status.HTTP_403_FORBIDDEN)
        # Get the user that will be followed
        followed_user = get_object_or_404(User, id=followed_user_id)

        # Check if the user is trying to follow themselves
        if followed_user == request.user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is already following the target user
        existing_follow = Follow.objects.filter(follower=request.user, followed=followed_user)

        if existing_follow.exists():
            # Log the issue and return the response
            print(f"[DEBUG] User {request.user.username} is already following {followed_user.username}.")
            return Response({"message": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new follow relationship
        Follow.objects.create(follower=request.user, followed=followed_user)

        # Log the successful creation of the follow relationship
        print(f"[DEBUG] User {request.user.username} successfully followed {followed_user.username}.")

        # Return a response indicating successful follow
        return Response({"message": f"You have successfully followed {followed_user.username}."}, status=status.HTTP_201_CREATED)
    
class UnfollowView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request, followed_user_id):
        # Get the user that will be unfollowed
        followed_user = get_object_or_404(User, id=followed_user_id)
        
        # Check if the user is trying to unfollow themselves
        if followed_user == request.user:
            return Response({"error": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the follow relationship exists
        follow = Follow.objects.filter(follower=request.user, followed=followed_user)
        if not follow.exists():
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete the follow relationship
        follow.delete()

        return Response({"message": f"You have unfollowed {followed_user.username}"}, status=status.HTTP_200_OK)

class UserFollowView(APIView):
    authentication_classes = [TokenAuthentication]
    
    def get(self, request, user_id):
        # Get the user whose followers and following we want to display
        user = User.objects.get(id=user_id)

        # Get the list of followers (people who follow this user)
        followers = Follow.objects.filter(followed=user).values_list('follower', flat=True)
        follower_users = User.objects.filter(id__in=followers)

        # Get the list of following (people this user follows)
        following = Follow.objects.filter(follower=user).values_list('followed', flat=True)
        following_users = User.objects.filter(id__in=following)

        # Prepare the response data
        followers_data = [user.username for user in follower_users]
        following_data = [user.username for user in following_users]

        # Return the response with followers and following
        return Response({
            "followers": followers_data,
            "following": following_data
        })
