from user.models import User

from django.db import models

class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    #location
    date = models.DateField(null=True) #날짜
    emoji = models.CharField(max_length=128, null=True) #기분
    content = models.TextField(null=True) #기록 내용
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True) #사진

    class Meta:
        db_table = 'memories'
        verbose_name = 'Memory'
        verbose_name_plural = 'Memories'
        ordering = ['id']


