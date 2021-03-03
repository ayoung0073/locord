from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import Memory, User
from .serializers import MemorySerializer

permission_classes = [IsAuthenticated]

# Create your views here.
class MemoryList(APIView):
    """
    List all Memory or create a new Memory
    """
    def get(self, request, format=None):
        # memories = Memory.objects.all()
        user_id = User.objects.get(email=request.user).id
        memories = Memory.objects.filter(user_id=user_id)
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)

    def post(self, request):
        request.data._mutable = True # 임시로 mutable 변경
        request.data['user'] = User.objects.get(email=request.user).id # 인증된 사용자 정보 저장
        request.data._mutable = False

        serializer = MemorySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class MemoryDetail(APIView):
    """
    Retrieve, update or delete a Memory instance
    """

    def get_object(self, pk):
        try:
            return Memory.objects.get(pk=pk)
        except Memory.DoesNotExist:
            raise Http404

    def check_user(self, request, pk):
        memory = self.get_object(pk)
        if memory.user_id != User.objects.get(email=request.user).id:
            return False, None
        request.data._mutable = True # 인증되면, request.data.user 설정
        request.data['user'] = memory.user_id
        request.data._mutable = False
        return True, memory

    def get(self, request, pk, format=None):
        check = self.check_user(request, pk)
        if not check[0]:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = MemorySerializer(check[1])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        check = self.check_user(request, pk)
        if not check[0]:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = MemorySerializer(check[1], data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        check = self.check_user(request, pk)
        if not check[0]:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        check[1].delete()
        return Response(status=status.HTTP_204_NO_CONTENT)