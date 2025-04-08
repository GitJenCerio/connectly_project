from posts.models import Post, Follow
from django.db.models import Q

class FeedFactory:
    def __init__(self, user):
        self.user = user

    def is_authenticated(self):
        return getattr(self.user, 'is_authenticated', False)

    def get_feed(self, filter_param=None):
        if filter_param:
            filter_param = filter_param.lower().strip()

        # ✅ STRICT ISOLATION: Only public posts if user is not authenticated
        if not self.is_authenticated():
            return Post.objects.filter(privacy='public') \
                .order_by('-created_at') \
                .select_related('author') \
                .prefetch_related('post_likes_related', 'comments')

        # ✅ AUTHENTICATED USERS
        if filter_param == 'liked':
            posts = Post.objects.filter(post_likes_related__user=self.user).distinct()

        elif filter_param == 'followed':
            followed_users_ids = Follow.objects.filter(follower=self.user).values_list('followed_id', flat=True)
            posts = Post.objects.filter(author_id__in=followed_users_ids, privacy='public')

        elif filter_param == 'private':
            posts = Post.objects.filter(author=self.user, privacy='private')

        elif filter_param == 'public':
            posts = Post.objects.filter(privacy='public')

        else:
            posts = Post.objects.filter(
                Q(privacy='public') |
                Q(author_id=self.user.id)  # ✅ USE author_id, not author=self.user
            )

        return posts.order_by('-created_at') \
                    .select_related('author') \
                    .prefetch_related('post_likes_related', 'comments')
