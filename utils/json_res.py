# 因为json默认不支持datetime类型数据，所以自定义json编码器
import json
import datetime
from django.http import JsonResponse

from .res_code import Code


# json编码器
# 自定义序列化器，处理时间字段
class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.astimezone().strftime('%Y-%m-%d %H:%M:%S')  # 转换为本地时间


def json_response(errno=Code.OK, errmsg='', data=None, kwargs=None):
    json_dict = {
        'errno': errno,
        'errmsg': errmsg,
        'data': data
    }
    if kwargs and isinstance(kwargs, dict):
        json_dict.update(kwargs)

    return JsonResponse(json_dict, encoder=MyJSONEncoder)
