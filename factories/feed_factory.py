# feed_factory.py

from posts.models import Post, PostLike, Follow
from django.db.models import Q

class FeedFactory:
    def __init__(self, user):
        self.user = user

    def get_feed(self, filter_param=None):
        """
        Retrieves posts based on the filter parameter.
        :param filter_param: A string like 'liked' or 'followed'
        :return: Queryset of posts visible to the user
        """
        if filter_param:
            filter_param = filter_param.lower().strip()

        if filter_param == 'liked':
            # Get posts that the user has liked
            posts = Post.objects.filter(post_likes_related__user__id=self.user.id).distinct()
        elif filter_param == 'followed':
            # Get posts from followed users
            followed_users_ids = Follow.objects.filter(follower=self.user).values_list('followed_id', flat=True)
            posts = Post.objects.filter(author_id__in=followed_users_ids)
        else:
            # All posts (restricted by privacy)
            posts = Post.objects.all()

        # Enforce privacy: show only public posts or private posts authored by user
        posts = posts.filter(Q(privacy='public') | Q(author=self.user))

        # Order and optimize
        posts = posts.order_by('-created_at').prefetch_related('post_likes_related', 'comments')
        return posts