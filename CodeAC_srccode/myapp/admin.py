from django.contrib import admin
from myapp.models import *
# Register your models here.
from django.contrib.auth.models import Group

admin.site.unregister(Group)

# Register your models here.
admin.site.register(User)
admin.site.register(DataSource)

admin.site.site_header = '气象观测点数据可视化平台后台登录'  # 设置header
admin.site.site_title = '气象观测点数据可视化平台后台登录'   # 设置title
admin.site.index_title = '气象观测点数据可视化平台后台登录'