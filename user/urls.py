from django.urls import path
from . import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token
urlpatterns = [
    path('signup', views.signup),
    path('login', obtain_jwt_token), # 로그인(토큰 발급)
    path('refresh', refresh_jwt_token), # 토큰 갱신(재발급) # 만료 전 요청해야함
    path('verify', verify_jwt_token), # 토큰 유효한지 검사

    path('login/kakao', views.oauth_kakao), 
    path('login/google', views.oauth_google)
]