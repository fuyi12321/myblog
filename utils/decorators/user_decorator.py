def my_decorator(func):
    def wrapper(request, *args, **kwargs):
        print('这是自定义装饰器')
        print('校验用户数据')
        return func(*args, **kwargs)
    return wrapper
