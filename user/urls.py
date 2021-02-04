from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),
    path('login/kakao/callback', views.oauth) # ,name='oauth

]