from django import forms
from django.core.validators import RegexValidator
from django_redis import get_redis_connection
from users.models import Users


class CheckImagForm(forms.Form):
    """
    check image code
    """
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    # 创建手机号的正则校验器
    mobile_validator = RegexValidator(r'^1[3-9]\d{9}$', '手机号码格式不正确')
    # 长度校验，正则校验，为空校验
    mobile = forms.CharField(max_length=11, min_length=11, validators=[mobile_validator, ],
                             error_messages={
                                 'max_length': '手机长度有误',
                                 'min_length': '手机长度有误',
                                 'required': '手机号不能为空'
                             })
    image_code_id = forms.UUIDField(error_messages={"required": "图片UUID不能为空"})
    captcha = forms.CharField(max_length=4, min_length=4,
                              error_messages={
                                  'max_length': '验证码长度有误',
                                  'min_length': '图片验证码长度有误',
                                  'required': '图片验证码不能为空'
                              })

    # 单独校验
    def clean_mobile(self):
        tel = self.cleaned_data.get('mobile')
        if Users.objects.filter(mobile=tel).count():
            raise forms.ValidationError("手机号已经注册，请重新输入")
        return tel

    # 联合校验
    def clean(self):
        clean_data = super().clean()
        mobile = clean_data.get('mobile')
        image_uuid = clean_data.get('image_code_id')
        captcha = clean_data.get('captcha')
        # 1.获取图片验证码
        try:
            con_redis = get_redis_connection(alias='verify_codes')
        except Exception as e:
            raise forms.ValidationError("未知错误{}".format(e))
        img_key = "img_{}".format(image_uuid).encode('utf8')
        image_code_origin = con_redis.get(img_key)
        con_redis.delete(img_key)
        real_image_code = image_code_origin.decode('utf8') if image_code_origin else None
        # 2.校验图片验证码
        if (not real_image_code) or (real_image_code.upper() != captcha.upper()):
            raise forms.ValidationError('图片验证码校验失败！')
        # 3.校验是否在60秒内已发送过短信
        sms_flag_fmt = "sms_flag_{}".format(mobile).encode('utf8')
        sms_flag = con_redis.get(sms_flag_fmt)
        if sms_flag:
            raise forms.ValidationError('获取短信验证码过于频繁')
