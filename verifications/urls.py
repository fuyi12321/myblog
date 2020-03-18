# /image_code/<uuid:image_code_id>
from django.urls import path, re_path
from . import views


# url的命名空间
app_name = 'verification'

urlpatterns = [
    path('image_codes/<uuid:image_code_id>/', views.ImageCode.as_view(), name='image_code'),
    # P命名username
    re_path('username/(?P<username>\w{5,20})/', views.CheckUsernameView.as_view(), name='check_username'),
    re_path('mobile/(?P<mobile>1[3-9]\d{9})/', views.check_mobile_view, name='check_mobile'),
    path('sms_code/', views.SmsCodeView.as_view(), name='sms_code'),
]
