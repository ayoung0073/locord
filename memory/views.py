from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.http import Http404
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import Memory
from .serializers import MemorySerializer
#from .permissions import IsAuthenticatedOrSuperUser

# Create your views here.
class MemoryList(APIView):
    """
    List all Memory or create a new Memory
    """
    permission_classes = [AllowAny]


    def get(self, request, format=None):
        memories = Memory.objects.all()
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MemorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class MemoryDetail(APIView):
    """
    Retrieve, update or delete a Memory instance
    """
    permission_classes = [AllowAny]


    def get_object(self, pk):
        try:
            return Memory.objects.get(pk=pk)
        except Memory.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        memory = self.get_object(pk)
        serializer = MemorySerializer(memory)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        memory = self.get_object(pk)
        serializer = MemorySerializer(memory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        memory = self.get_object(pk)
        memory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)