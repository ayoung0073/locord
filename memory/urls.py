from django.urls import path, include
from . import views
from rest_framework import routers
from .views import MemoryViewSet

router = routers.DefaultRouter()
router.register(r'memories', MemoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
