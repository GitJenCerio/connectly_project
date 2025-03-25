# posts/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from .models import User, Post, Comment, PostLike, CommentLike
from .serializers import (
    UserSerializer, PostSerializer, CommentSerializer,
    PostLikeSerializer, CommentLikeSerializer
)
from .permissions import IsAuthorOrReadOnly
from factories.post_factory import PostFactory



# -----------------------------
#   USER VIEWS
# -----------------------------
from singletons.logger_singleton import LoggerSingleton


logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")


class UserListCreate(APIView):
 def get(self, request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
 
 def post(self, request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,
        status=status.HTTP_201_CREATED)
    return Response(serializer.errors,
    status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]  # Allow only authenticated users + object-level permission

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # `IsAuthorOrReadOnly` will automatically deny access if the user is not the author
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            logger.info(f"Updated user: {updated_user.username}")
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        # `IsAuthorOrReadOnly` will automatically deny access if the user is not the author
        logger.info(f"Deleted user: {user.username}")
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# -----------------------------
#   POST VIEWS
# -----------------------------
class CreatePostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        user = request.user  # Correctly access the authenticated user

        if not user.is_authenticated:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # Debugging - Ensure the user is a valid instance
        print(f"Authenticated user: {user}")
        if not isinstance(user, User):
            return Response({'error': 'Invalid user instance'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {}),
                author=user  # Pass the authenticated user as the author
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            updated_post = serializer.save()
            logger.info(f"Updated post: {updated_post.title}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        logger.info(f"Deleted post: {post.title}")
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------
#   POST LIKE VIEWS
# -----------------------------
class PostLikeListCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        logger.info(f"Removing like from {post_like.user.username} on {post_like.post.title}")
        post_like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        comment_like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)