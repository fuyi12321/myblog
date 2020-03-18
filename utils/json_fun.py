from django.http import JsonResponse

from .res_code import Code


def json_response(errno=Code.OK, errmsg='', data=None, **kwargs):
    json_dict = {
        'errno': errno,
        'errmsg': errmsg,
        'data': data
    }
    if kwargs and isinstance(kwargs, dict) and kwargs.keys():
        json_dict.update(kwargs)

    return JsonResponse(json_dict)
