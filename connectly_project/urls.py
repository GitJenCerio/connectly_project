"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



# connectly_project/urls.py
from django.contrib import admin
from django.urls import path, include
from posts.views_auth import CustomObtainAuthToken
from posts.views import GoogleLogin
from posts.views import NewsFeedView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('posts.urls')),  # your existing API endpoints
    path('api/login/', CustomObtainAuthToken.as_view(), name='api-login'),
    path('auth/google/login/', GoogleLogin.as_view(), name='google-login'),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('allauth.socialaccount.urls')),
   
]