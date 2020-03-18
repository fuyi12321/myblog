import re

from django import forms
from django.db.models import Q
from django_redis import get_redis_connection
from django.contrib.auth import login, logout

from .models import Users
from verifications.constants import SMS_CODE_LENGTH, USER_SESSION_EXPIRY


class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, min_length=5,
                               error_messages={
                                   'max_length': '用户名长度要小于20',
                                   'min_length': '用户名长度要大于4',
                                   'required': '用户名不能为空'
                               })
    password = forms.CharField(label='密码', max_length=20, min_length=6,
                               error_messages={
                                   'max_length': '密码长度要小于20',
                                   'min_length': '密码长度要大于5',
                                   'required': '用户名不能为空'
                               })
    password_repeat = forms.CharField(label='确认密码', max_length=20, min_length=6,
                                      error_messages={
                                          'max_length': '密码长度要小于20',
                                          'min_length': '密码长度要大于5',
                                          'required': '用户名不能为空'
                                      })
    mobile = forms.CharField(label='手机号码', max_length=11, min_length=11,
                             error_messages={
                                 'max_length': '手机号码长度有误',
                                 'min_length': '手机号码长度有误',
                                 'required': '手机号码不能为空'
                             })
    sms_code = forms.CharField(label='短信验证码', max_length=SMS_CODE_LENGTH, min_length=SMS_CODE_LENGTH,
                               error_messages={
                                   'max_length': '短信验证码长度有误',
                                   'min_length': '短信验证码长度有误长度有误',
                                   'required': '短信验证码不能为空'
                               })

    def clean_username(self):
        """
        校验用户名
        :return:
        """
        username = self.cleaned_data.get('username')
        if Users.objects.filter(username=username).exists():
            return forms.ValidationError('用户名已存在！')
        return username

    def clean_mobile(self):
        """
        校验手机号
        :return:
        """
        mobile = self.cleaned_data.get('mobile')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise forms.ValidationError('手机号码格式不正确')

        if Users.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError('手机号码已注册！')

        return mobile

    def clean(self):
        """
        校验，密码，和短信验证码
        :return:
        """
        clean_data = super().clean()
        # 校验密码是否一致
        password = clean_data.get('password')
        password_repeat = clean_data.get('password_repeat')
        if password != password_repeat:
            raise forms.ValidationError('两次密码不一致！')

        # 校验短信验证码
        sms_code = clean_data.get('sms_code')
        mobile = clean_data.get('mobile')

        redis_conn = get_redis_connection(alias='verify_codes')
        # 创建保存短信验证码的标记key
        real_code = redis_conn.get('sms_text_{}'.format(mobile))
        if (not real_code) or (real_code.decode('utf-8') != sms_code):
            raise forms.ValidationError('短信验证码错误!')


class LoginForm(forms.Form):
    # 手机号或用户名
    account = forms.CharField(error_messages={'required': '账户不能为空'})
    password = forms.CharField(max_length=20, min_length=6,
                               error_messages={
                                   'max_length': '密码长度要小于20',
                                   'min_length': '密码长度要大于6',
                                   'require': '密码不能为空'
                               })
    remember = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_account(self):
        """
        校验用户账户
        :return:
        """
        account = self.cleaned_data.get('account')
        if not re.match(r'^1[3-9]\d{9}$', account) and (len(account) < 6 or len(account) > 20):
            raise forms.ValidationError('用户账户格式不正确，请重新输入')
        # 一定要return
        return account

    def clean(self):
        """
        校验用户名密码，并实现登录逻辑
        :return:
        """
        # 1.获取清洗之后的参数
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        password = cleaned_data.get('password')
        remember = cleaned_data.get('remember')

        # 获取数据库的账号和密码并判断
        user_queryset = Users.objects.filter(Q(mobile=account) | Q(username=account))
        if user_queryset:
            user = user_queryset.first()
            if user.check_password(password):
                # 是否将用户信息设置到会话中
                if remember:
                    self.request.session.set_expiry(USER_SESSION_EXPIRY)
                else:
                    self.request.session.set_expiry(0)
                # 登录
                login(self.request, user)
            else:
                raise forms.ValidationError('用户名密码错误!')
        else:
            raise forms.ValidationError('用户账号不存在，请重新输入!')
