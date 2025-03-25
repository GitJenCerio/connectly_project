from posts.models import Post
from django.contrib.auth.models import User


class PostFactory:
    @staticmethod
    def create_post(post_type, title, content='', metadata=None, author=None):
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError("Invalid post type")

        # Validate type-specific requirements
        if post_type == 'image' and 'file_size' not in metadata:
            raise ValueError("Image posts require 'file_size' in metadata")
        if post_type == 'video' and 'duration' not in metadata:
            raise ValueError("Video posts require 'duration' in metadata")

        # Ensure the author is set (could be user or other logic)
        if not author or not isinstance(author, User):
            raise ValueError("Post must have a valid author (User instance)")

        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata,
            author=author  # Save the author (the user who created the post)
        )
