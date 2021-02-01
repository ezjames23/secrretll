"""Defines url patterns for users """

from django.urls import path, include 
from django.contrib.auth import views as auth_views
from . import views 

app_name = "users"

urlpatterns = [
    # login
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name = 'login'),
    # logout
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html', next_page=None), name = 'logout'),
    # register
    path('register/', views.register, name='register'),
]