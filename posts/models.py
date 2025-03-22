from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.username


class Post(models.Model):
    POST_TYPES = [
        ('blog', 'Blog'),
        ('announcement', 'Announcement'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    metadata = models.JSONField(blank=True, null=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post_type.capitalize()} by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

from django.db import models
from django.contrib.auth.models import User

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

