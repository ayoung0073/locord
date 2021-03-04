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
from django_filters.rest_framework import FilterSet, filters, DjangoFilterBackend

class MemoryViewSet(viewsets.ModelViewSet):
    serializer_class = MemorySerializer
    filter_fields = ('lon', 'lat')
    permission_classes = [IsAuthenticated]
    queryset = Memory.objects.all()

    #GET memories/user-memory -> 각 사용자의 memory 객체 반환
    @action(detail=False, url_path='user-memory')
    def user_memory(self, request):
        user_id = User.objects.get(email=request.user).id
        memories = self.filter_queryset(self.get_queryset()).filter(user_id=user_id) #filter
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)

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

    #PATCH 특정 memory 객체 수정
    def partial_update(self, request, *args, **kwargs):
        request.data._mutable = True  # 임시로 mutable 변경
        request.data['user'] = User.objects.get(email=request.user).id  # 인증된 사용자 정보 저장
        request.data._mutable = False

        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
