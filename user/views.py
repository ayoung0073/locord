from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, status

from .serializers import UserCreateSerializer, UserLoginSerializer
from .models import User
from django.contrib.auth import models

from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate

from rest_framework_jwt.settings import api_settings

import requests
import json

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

class KakaoException(Exception):
    pass

class TokenException(Exception):
    pass

class GoogleException(Exception):
    pass

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response({"message": "Request Body Error."}, status=status.HTTP_409_CONFLICT)
        if serializer.validated_data['email'] == "None":
            return Response({'message': 'fail'}, status=status.HTTP_200_OK)

        response = {
            'success': True,
            'token': serializer.data['token']
        }
        return Response(response, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_kakao(request):
    try:
        code = request.GET['code']
        print('code = ' + str(code))

        secret_file = os.path.join(BASE_DIR, 'secrets.json')

        with open(secret_file) as f:
            secrets = json.loads(f.read())
        def get_secret(setting, secrets=secrets):
            try:
                return secrets[setting]
            except KeyError:
                error_msg = "Set the {} environment variable".format(setting)
                raise ImproperlyConfigured(error_msg)

        KAKAO_CLIENT_ID = get_secret("KAKAO_CLIENT_ID")
        #KAKAO_CLIENT_SECRET = get_secret("KAKAO_CLIENT_SECRET")

        redirect_uri = 'http://127.0.0.1:8000/user/login/kakao/callback'
        # 토큰 받아오기
        access_token_request_uri = 'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&'
        access_token_request_uri += 'client_id=' + KAKAO_CLIENT_ID
        access_token_request_uri += '&code=' + code
        access_token_request_uri += '&redirect_uri=' + redirect_uri
        # access_token_request_uri += '&client_secret=' + client_secret

        try:
            access_token_request_uri_data = requests.get(access_token_request_uri)
            json_data = access_token_request_uri_data.json()
            print(json_data)
            access_token = json_data.get('access_token', None)

            if access_token is None:
                raise TokenException()

            # 프로필 정보 받아오기
            headers = ({'Authorization' : f"Bearer {access_token}"})


        except TokenException:
            response = {
                'success':False,
                'message':'카카오 인증 실패'
            }
            return Response(response, status=500)

            
        user_profile_info_uri = 'https://kapi.kakao.com/v2/user/me'
        user_profile_info = requests.get(user_profile_info_uri, headers=headers)

        json_data = user_profile_info.json() 
        print(json_data)    
        kakao_account = json_data.get('kakao_account')

        kakao_profile = kakao_account.get('profile')
        nickname = kakao_profile.get('nickname', None)
        email = kakao_account.get('email', None)


        if email is None:
            raise KakaoException() # 이메일은 필수제공 항목이 아니어서, 수정 필요함

        if nickname is None:
            nickname = email # 이름이 비어있는 경우, email로 대체

        print(nickname, email)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            print('login')

        else:
            user = User.objects.create(
                email=email,
                nickname=nickname,
                oauth=2
            )
            user.save()

        payload = JWT_PAYLOAD_HANDLER(user)
        jwt_token = JWT_ENCODE_HANDLER(payload)

        response = {
            'success' : True, 
            'token' : jwt_token
        }

        return Response(response, status=200)

    except KakaoException:
        response = {
            'success':False,
            'message':'이메일은 필수 항목입니다.'
        }
        return Response(response, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_google(request):
    try:
        code = request.GET['code']
        print('code = ' + str(code))

        secret_file = os.path.join(BASE_DIR, 'secrets.json')

        with open(secret_file) as f:
            secrets = json.loads(f.read())
        def get_secret(setting, secrets=secrets):
            try:
                return secrets[setting]
            except KeyError:
                error_msg = "Set the {} environment variable".format(setting)
                raise ImproperlyConfigured(error_msg)

        GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
        GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")

        redirect_uri = 'http://127.0.0.1:8000/user/login/google/callback'

        headers = ({'Authorization' : f"Bearer {code}"})

        # 토큰 받아오기
        access_token_request_uri = 'https://oauth2.googleapis.com/token?grant_type=authorization_code'
        access_token_request_uri += '&client_id=' + GOOGLE_CLIENT_ID
        access_token_request_uri += '&client_secret=' + GOOGLE_CLIENT_SECRET
        access_token_request_uri += '&code=' + code
        access_token_request_uri += '&redirect_uri=' + redirect_uri
        access_token_request_uri += '&scope=https://www.googleapis.com/auth/userinfo.profile'

        try:
            access_token_request_uri_data = requests.post(access_token_request_uri, headers=headers)
            json_data = access_token_request_uri_data.json()

            access_token = json_data.get('access_token', None)

            if access_token is None:
                raise TokenException()

        except TokenException:
            response = {
                'success':False,
                'message':'구글 인증 실패'
            }
            return Response(response, status=500)


        # 프로필 정보 받아오기
        headers = ({'Authorization' : f"Bearer {access_token}"})

        user_profile_info_uri = 'https://www.googleapis.com/oauth2/v3/userinfo'
        user_profile_info = requests.get(user_profile_info_uri, headers=headers)

        json_data = user_profile_info.json() 
        # print(json_data)    
        nickname = json_data.get('name', None)
        email = json_data.get('email', None)

        if email is None:
            raise GoogleException()

        if nickname is None:
            nickname = email

        print(nickname, email)


        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            print('login')
        else:
            user = User.objects.create(
                email=email,
                nickname=nickname,
                oauth=1
            )
            user.save()

        payload = JWT_PAYLOAD_HANDLER(user)
        jwt_token = JWT_ENCODE_HANDLER(payload)

        response = {
            'success' : True, 
            'token' : jwt_token
        }

        return Response(response, status=200)
        
    except GoogleException:
        response = {
            'success':False,
            'message':'이메일은 필수 항목입니다.'
        }
        return Response(response, status=400)

