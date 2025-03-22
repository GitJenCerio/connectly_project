from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory


@method_decorator(csrf_exempt, name='dispatch')
class UserListCreate(APIView):
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

@method_decorator(csrf_exempt, name='dispatch')
class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        print("✅ Reached the GET view!")
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)
        return Response({"content": post.content})
    
    
    def delete(self, request, pk):
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response({"message": "Post deleted!"}, status=204)


@method_decorator(csrf_exempt, name='dispatch')
class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        return Response({"message": "Authenticated!"})

logger = LoggerSingleton().get_logger()
logger.info("API initialized successfully.")


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from factories.post_factory import PostFactory


class CreatePostView(APIView):
    def post(self, request):
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
