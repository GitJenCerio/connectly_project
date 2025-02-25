from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Connectly API!")

# Include 'posts' app URLs
urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),  # Admin route
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
    path('posts/', include('posts.urls')),  # Routes for the posts app
]
