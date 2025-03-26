from rest_framework import serializers
from .models import User, Post, Comment, PostLike, CommentLike



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Include password

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
       
class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    comments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'post_type', 'created_at', 'author', 'comments'
        ]
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'text', 'author', 'created_at']
        read_only_fields = ['author', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)


class PostLikeSerializer(serializers.ModelSerializer):
    # Mark user as read-only to auto-assign from logged-in user
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        else:
            raise serializers.ValidationError("User not found in request context.")

        post = attrs.get('post')

        # Prevent liking your own post
        if post.author == user:
            raise serializers.ValidationError("You cannot like your own post.")

        # Check if the user already liked this post
        if PostLike.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("You have already liked this post.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class CommentLikeSerializer(serializers.ModelSerializer):
    # Mark user as read-only to auto-assign from logged-in user
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())

    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        else:
            raise serializers.ValidationError("User not found in request context.")

        comment = attrs.get('comment')

        # Prevent liking your own comment
        if comment.author == user:
            raise serializers.ValidationError("You cannot like your own comment.")

        # Check if the user already liked this comment
        if CommentLike.objects.filter(user=user, comment=comment).exists():
            raise serializers.ValidationError("You have already liked this comment.")

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)