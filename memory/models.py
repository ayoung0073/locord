from user.models import User

from django.db import models

class Memory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    #location
    date = models.DateField(null=True)
    emoji = models.CharField(max_length=128, null=True)
    content = models.TextField(null=True)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True)

    class Meta:
        db_table = 'memories'
        verbose_name = 'Memory'
        verbose_name_plural = 'Memories'
        ordering = ['id']


