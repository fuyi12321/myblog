import json
import logging
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib.auth import login, logout

from .forms import RegisterForm, LoginForm
from .models import Users

from utils.json_fun import json_response
from utils.res_code import Code, error_map


logger = logging.getLogger('django')


# Create your views here.
class RegisterView(View):
    """
    user/register
    # 1.创建一个类
    """
    # 2.创建get
    def get(self, request):
        return render(request, 'users/register.html')

    # 3.创建post
    def post(self, request):
        # 4.获取前端传过来的参数
        try:
            json_data = request.body
            if not json_data:
                return json_response(errno=Code.PARAMERR, errmsg="参数为空，请重新输入！")
            dict_data = json.loads(json_data.decode('utf8'))
        except Exception as e:
            logger.info('错误信息:\n{}'.format(e))
            return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR] + e)
        form = RegisterForm(dict_data)
        # 5.校验参数
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            # 6.将用户信息保存到数据库
            user = Users.objects.create_user(username=username, password=password, mobile=mobile)
            login(request, user)
            # 7.将结果返回前端
            return json_response(errmsg='恭喜你，注册成功！')
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_msg_str = '/'.join(err_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=err_msg_str)


class LoginView(View):
    """
    登录视图
    """
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        # 2.接收参数
        try:
            json_data = request.body
            if not json_data:
                return json_response(errno=Code.PARAMERR, errmsg="参数为空，请重新输入！")
            dict_data = json.loads(json_data.decode('utf8'))
        except Exception as e:
            logger.info('错误信息:\n{}'.format(e))
            return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR] + e)
        # 3.校验参数
        form = LoginForm(data=dict_data, request=request)
        if form.is_valid():
            return json_response(errmsg='恭喜登录成功！')
        else:
            err_msg_list = []
            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_msg_str = '/'.join(err_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=err_msg_str)


class LogoutView(View):
    """
    登出视图
    """
    def get(self, request):
        logout(request)
        return redirect(reverse('users:login'))
