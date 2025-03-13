from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post
from .permissions import IsPostAuthor  # Import the custom permission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create user using the data from the request
        username = request.data.get("username")
        password = request.data.get("password")  # Password should be hashed automatically

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user with password encryption
        user = User.objects.create_user(username=username, password=password)

        # Return the created user data in response (excluding password)
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_201_CREATED)
        
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

class UserLogin(APIView):
    def post(self, request):
        # Extract username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in (sets sessionid cookie)
            login(request, user)  # This should set the session cookie

            # Manually check if session exists
            session_id = request.session.session_key
            if session_id:
                print("Session ID set:", session_id)
            else:
                print("No session ID set")

            return Response({"message": "Authentication successful!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
class PostDetailView(APIView):
    # Use IsAuthenticated and IsPostAuthor permissions
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        # Get the post object by primary key
        post = Post.objects.get(pk=pk)
        
        # Check if the user has permission to access the post
        self.check_object_permissions(request, post)
        
        # Return the post content if permission is granted
        return Response({"content": post.content})
    
class ProtectedView(APIView):
    # Require TokenAuthentication and IsAuthenticated permission for this view
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})