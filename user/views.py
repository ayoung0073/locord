from rest_framework import status
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
def oauth(request):
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

    access_token_request_uri_data = requests.get(access_token_request_uri)
    json_data = access_token_request_uri_data.json()
    print(json_data)
    access_token = json_data['access_token']

    # 프로필 정보 받아오기
    headers = ({'Authorization' : f"Bearer {access_token}"})

    user_profile_info_uri = 'https://kapi.kakao.com/v2/user/me'
    user_profile_info = requests.get(user_profile_info_uri, headers=headers)

    json_data = user_profile_info.json() 
    print(json_data)    
    nickname = json_data['kakao_account']['profile']['nickname']
    email = json_data['kakao_account']['email']

    print(nickname, email)


    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print('login')
    else:
        user = User.objects.create(
            email=email,
            nickname=nickname
        )
        user.save()

    payload = JWT_PAYLOAD_HANDLER(user)
    jwt_token = JWT_ENCODE_HANDLER(payload)

    response = {
        'success' : True, 
        'token' : jwt_token
    }

    return Response(response, status=200)
