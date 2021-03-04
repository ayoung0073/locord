from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import Http404
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import Memory, User
from .serializers import MemorySerializer

permission_classes = [IsAuthenticated]

# Create your views here.

class MemoryViewSet(viewsets.ModelViewSet):
    serializer_class = MemorySerializer
    queryset = Memory.objects.all()

    #각각의 사용자들의 memories 반환 & 필터링
    @action(detail=False, url_path='user-memory') #GET 특정 사용자의 객체들
    def user_memory(self, request):
        user_id = User.objects.get(email=request.user).id
        memories = Memory.objects.filter(user_id=user_id)
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)

    #post 시 설정 -> user_id 부분 넣어줘야 함
    def create(self, request, *args, **kwargs):
        request.data._mutable = True # 임시로 mutable 변경
        request.data['user'] = User.objects.get(email=request.user).id  # 인증된 사용자 정보 저장
        request.data._mutable = False

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    """
    def check_user(self, request, pk):
        memory = self.get_object(pk)
        if memory.user_id != User.objects.get(email=request.user).id:  # 요청한 사용자와 memory의 user가 다를 때
            return False, None
        request.data._mutable = True  # 인증되면, request.data.user 설정
        request.data['user'] = memory.user_id
        request.data._mutable = False
        return True, memory
    """

    #PATCH 특정 memory 객체 수정 partial update ?
    def partial_update(self, request, *args, **kwargs):
        request.data._mutable = True  # 임시로 mutable 변경
        request.data['user'] = User.objects.get(email=request.user).id  # 인증된 사용자 정보 저장
        request.data._mutable = False

        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
