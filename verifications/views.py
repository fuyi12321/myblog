# 最上面是python内置的模块
import logging
import json
import random
# 第二部分是框架的包
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
# 第三部分是我们自己的模块
from utils.captcha.captcha import captcha
from . import constants
from users.models import Users
from utils.json_fun import json_response
from utils.res_code import Code, error_map
from utils.yuntongxun.sms import CCP
from . import forms

# 导入日志器
logger = logging.getLogger('django')


# Create your views here.
# 1.创建一个类视图
class ImageCode(View):
    """
    define image verification view
    /image_code/<uuid:image_code_id>
    """
    # 2.从前端获取参数UUID，并且校验
    def get(self, request, image_code_id):
        # 3.生成验证码和验证码图片
        text, image = captcha.generate_captcha()
        # 4.建立redis连接，并且将图片验证码保存到redis
        # 确保settings.py文件中配置redis CACHE
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_code_id)
        con_redis.setex(img_key, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        logger.info("Image code:{}".format(text))
        # 5.把验证码图片返回给前端,输出图片文件
        return HttpResponse(content=image, content_type='images/jpg')


# 1.创建一个类
class CheckUsernameView(View):
    """
    check whether the user exists
    """
    # 2.校验参数-url里
    def get(self, request, username):
        # 3.查询数据库是否有同名
        # user = Users.objects.filter(username=username)
        # 4.返回校验的结果
        # if user:
        #     return HttpResponse('可以注册')
        # else:
        #     return HttpResponse('不能注册')
        # 无则0 有则1
        count = Users.objects.filter(username=username).count()
        # try:
        #     count = Users.objects.get(username=username).count()
        # except ObjectDoesNotExist:
        #     return json_response(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        data = {
            'username': username,
            'count': count
        }
        return json_response(data=data)
        # return JsonResponse(data=data)


def check_mobile_view(request, mobile):
    """
    校验手机号是否存在
    url:/moblie/(?P<moblie>1[3-9]\d{9})/
    :param request:
    :param mobile:
    :return:
    """
    data = {
        'mobile': mobile,
        'count': Users.objects.filter(mobile=mobile).count()
    }
    return json_response(data=data)


# 1.创建一个类
class SmsCodeView(View):
    """
    发送短信验证码
    POST /sms_codes/
    业务流程分析
        - 检查图片验证码是否正确
        - 检查是否在60s内发送记录
        - 生成短信验证码
        - 发送短信
        - 保存短信验证码与发送记录
    """
    def post(self, request):
        # 2.获取前端参数
        json_data = request.body
        if not json_data:
            return json_response(errno=Code.PARAMERR, errmsg="参数为空，请重新输入")
        dict_data = json.loads(json_data.decode('utf8'))
        # 3.校验参数
        # mobile = dict_data.get('mobile')
        # text = dict_data.get('text')
        # image_code_id = dict_data.get('image_code_id')
        form = forms.CheckImagForm(dict_data, request=request)
        if form.is_valid():
            # 2.获取手机
            mobile = form.cleaned_data.get('mobile')
            # 3.生成手机验证码
            sms_code = ''.join([random.choice('0123456789') for _ in range(constants.SMS_CODE_LENGTH)])
            # 4.发送手机验证码
            # ccp = CCP()
            # try:
            #     res = ccp.send_template_sms(mobile,
            #                                 [sms_code, constants.SMS_CODE_YUNTX_EXPIRES],
            #                                 constants.SMS_CODE_TEMP_ID)
            #     if res == 0:
            #         logger.info('发送短信验证码[正常][mobile: %s sms_code: %s]' % (mobile, sms_code))
            #     else:
            #         logger.error('发送短信验证码[失败][moblie: %s sms_code: %s]' % (mobile, sms_code))
            #         return json_response(errno=Code.SMSFAIL, errmsg=error_map[Code.SMSFAIL])
            # except Exception as e:
            #     logger.error('发送短信验证码[异常][mobile: %s message: %s]' % (mobile, e))
            #     return json_response(errno=Code.SMSERROR, errmsg=error_map[Code.SMSERROR])
            logger.info('发送短信验证码[正常][mobile: %s sms_code: %s]' % (mobile, sms_code))

            # 5.保存到redis数据库
            # 创建短信验证码发送记录
            sms_flag_key = 'sms_flag_{}'.format(mobile).encode('utf8')
            # 创建短信验证码内容记录
            sms_text_key = 'sms_text_{}'.format(mobile).encode('utf8')
            redis_conn = get_redis_connection(alias='verify_codes')
            # 实例一个管道
            pl = redis_conn.pipeline()

            try:
                # 设置过期时间setex(key, seconds, value)
                pl.setex(sms_flag_key, constants.SMS_CODE_INTERVAL, 1)
                pl.setex(sms_text_key, constants.SMS_CODE_EXPIRES, sms_code)
                # 让管道通知redis执行命令
                pl.execute()
                return json_response(errmsg="短信验证码发送成功！")
            except Exception as e:
                logger.error('redis 执行异常：{}'.format(e))
                return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])

        else:
            # 将表单的报错信息进行拼接
            err_msg_list = []
            # 获取表单错误信息
            for item in form.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串

            return json_response(errno=Code.PARAMERR, errmsg=err_msg_str)
