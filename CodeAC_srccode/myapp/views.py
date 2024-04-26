from django.shortcuts import render, redirect
from myapp import visualization
from myapp.datasrc import MySQLTool
from django.http import FileResponse, HttpResponseNotFound
import os
from django.contrib.auth import logout, login, authenticate

from myapp.forms import RegForm, LoginForm
from myapp.models import *
from django.contrib.auth.hashers import make_password

def welcome(request):
    mysqlite = MySQLTool()
    df = mysqlite.read_station()
    # print(df)
    context = {
      'station_data': df.to_dict(orient='records'),  # 将DataFrame转为字典列表
    }
    return render(request, 'welcome.html', context)

def datashow(request):
    my = MySQLTool()
    name_stat_dict, name = my.dict_stat_name()
    print(name_stat_dict)
    city = request.GET.get('city', 'BAINGOIN, CH')
    stat = name_stat_dict[city]
    dew_conf, slp_conf, tmp_conf, vis_conf, dire_conf, sped_conf, reli, analy = visualization.spec_htmls(stat)
    # print("ok " + stat)
    context = {'stat': stat, 'dew_conf': dew_conf, 'slp_conf': slp_conf, 'tmp_conf': tmp_conf, 'vis_conf': vis_conf, 'dire_conf': dire_conf, 'sped_conf': sped_conf, 'reli': reli, 'name': name, 'city': city, 'analy': analy}
    return render(request, "showdata.html", context)
# visualization.spec_htmls("51828099999")

def download(request):
    # 获取当前文件所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # 构建完整文件路径
    file_path = os.path.join(current_directory, 'static', 'datasrc', 'data.sqlite')
    # 检查文件是否存在
    if os.path.exists(file_path):
        filename = 'data.sqlite'
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        # 文件不存在时返回404响应
        return HttpResponseNotFound("File not found")

def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                # print("ok")
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                    return redirect('welcome')
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        pass
    #登录成功到达
    return render(request, 'login.html', locals())
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(
                    username=reg_form.cleaned_data["username"],
                    email=reg_form.cleaned_data["email"],
                    password=make_password(reg_form.cleaned_data["password"]),
                )
                user.save()
                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend'  # 指定默认的登录验证方式
                login(request, user)
                # 注册成功到达
                return redirect('welcome')
            else:
                raise Exception(reg_form.errors)
        else:
            reg_form = RegForm()
    except Exception as e:
        pass
    return render(request, 'register.html', locals())

# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        pass
    return redirect(request.META['HTTP_REFERER'])