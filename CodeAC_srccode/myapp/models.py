from django.db import models
from django.contrib.auth.models import AbstractUser
import locale
from myapp import forms
# Create your models here.
# 首先是用户的数据模式
class User(AbstractUser):
    user_phone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    user_qq = models.CharField(max_length=20, blank=True, null=True, verbose_name='QQ号码')
    class Meta:
        # 添加以下两行，为groups和user_permissions指定related_name
        permissions = []
        default_permissions = []

class DataSource(models.Model):
    stat_date = models.CharField(max_length=50,primary_key=True)
    name = models.TextField()
    latitude = models.FloatField(null=True)  # 使用null=True允许数据库中该列的值为NULL
    longitude = models.FloatField(null=True)
    dew = models.TextField()
    slp = models.TextField()
    tmp = models.TextField()
    vis = models.TextField()
    wnd = models.TextField()

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'datasource'