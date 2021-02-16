from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),
    path('login/kakao', views.oauth_kakao), 
    path('login/google', views.oauth_google)
]