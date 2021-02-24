from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from . import views

urlpatterns = [
    path('memories/', views.MemoryList.as_view()),
    path('memories/<int:pk>/', views.MemoryDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)