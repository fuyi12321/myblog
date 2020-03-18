from datetime import datetime
import json
import logging
from urllib.parse import urlencode

from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import ContentType, Permission, models
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count

from admin import constans
from news.models import Tag, News
from utils import paginator_script
from utils.json_fun import json_response
from utils.decorators.user_decorator import my_decorator
from utils.res_code import Code, error_map
from utils.fastdfs.fdfs import FDFS_Client
from django.conf import settings

from .forms import NewsPubForm
from users.models import Users


logger = logging.getLogger('django')


class MyDecoratorMixin(object):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        view = my_decorator(view)
        return view


# class IndexView(MyDecoratorMixin, View):
class IndexView(LoginRequiredMixin, View):
    # login_url = 'users:login'
    redirect_field_name = 'next'

    # 多重继承mrc-c3算法
    def get(self, request):
        print(IndexView.__mro__)
        return render(request, 'admin/index/index.html')


# @my_decorator
# @login_required(login_url='users:login')
# @permission_required('news.delete_news', raise_exception=True)
# def index_fn(request):
#     return HttpResponse('大家是python的大牛')

# index_fn = my_decorator(index_fn)
# @method_decorator(login_required(login_url='users:login'), name='dispatch')


class TagManageView(PermissionRequiredMixin, View):
    """
    route:/admin/tags/
    """
    permission_required = ('news.add_tag', 'news.view_tag')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_response(errno=Code.ROLEERR, errmsg="没有操作权限")
        else:
            return super(TagManageView, self).handle_no_permission()

    # 给一个模型的所有权限
    def get_permission_required(self):
        # content_type 对应的是模型
        content_type = ContentType.objects.get_for_model(Tag)
        permissions = Permission.objects.filter(content_type=content_type)

    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(news_num=Count('news')).\
            filter(is_delete=False).order_by('-news_num', 'update_time')

        return render(request, 'admin/news/tags_manage.html', context={
            'tags': tags
        })


class TagEditView(PermissionRequiredMixin, View):
    permission_required('news.change_tag', 'news.delete_tag')
    raise_exception = True

    def handle_no_permission(self):
        return json_response(errno=Code.ROLEERR, errmsg="没有操作权限")

    def delete(self, request, tag_id):
        tag = Tag.objects.only('id').filter(is_delete=False, id=tag_id).first()
        if tag:
            tag.is_delete = True
            tag.save(update_fields=['is_delete'])
            return json_response(errmsg="标签删除成功")
        else:
            return json_response(errno=Code.PARAMERR, errmsg="需要删除的标签不存在")

    def put(self, request, tag_id):
        json_data = request.body
        if not json_data:
            return json_response(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        tag = Tag.objects.only('id').filter(id=tag_id).first()
        if tag:
            if tag_name:
                tag_name = tag_name.strip()
                if not Tag.objects.only('id').filter(name=tag_name).exits():
                    tag.name = tag_name
                    tag.save(updata_fields=['name'])
                    return json_response(errmsg="标签更新成功")
                else:
                    return json_response(errno=Code.PARAMERR, errmsg="标签名已存在")
            else:
                return json_response(errno=Code.PARAMERR, errmsg="标签名不能为空")
        else:
            return json_response(errno=Code.PARAMERR, errmsg="需要更新的标签不存在")

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_response(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))
        tag_name = dict_data.get('name')
        if tag_name:
            tag_name = tag_name.strip()
            tag_tuple = Tag.objects.get_or_create(name=tag_name)
            tag_instance, tag_created_bool = tag_tuple
            new_tag_dict = {
                "id": tag_instance.id,
                "name": tag_instance.name
            }
            return json_response(errmsg="标签添加成功", data=new_tag_dict) if tag_created_bool else\
                json_response(errno=Code.DATAEXIST, errmsg="标签名已存在")
        else:
            return json_response(errno=Code.PARAMERR, errmsg="标签名为空")


# class Test(PermissionRequiredMixin, View):
#     permission_required('news.change_tag')
#     raise_exception = True
#
#     def handle_no_permission(self):
#         return json_response()
#
#     def get(self, request):
#         return json_response()


class NewsManageView(LoginRequiredMixin, View):
    """
    route: /admin/news/
    """
    permission_required('news.add_news', 'news.view_news')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return json_response(errno=Code.ROLEERR, errmsg="没有操作权限")
        else:
            return super(NewsManageView, self).handle_no_permission()

    def get(self, request):
        # 1.获取文章标签
        # 2.从前端获取参数
        # 3.通过过滤条件，去数据库查询
        # 4.分页操作
        # 5.模板渲染
        # 链式 惰性查询
        tags = Tag.objects.only('id', 'name').filter(is_delete=False)
        news = News.objects.only('id', 'title', 'author__username', 'tag__name', 'update_time').\
            select_related('author', 'tag').filter(is_delete=False)

        try:
            start_time = request.GET.get('start_time', '')
            start_time = datetime.strptime(start_time, '%Y/%m/%d') if start_time else ''

            end_time = request.GET.get('end_time', '')
            end_time = datetime.strptime(end_time, '%Y/%m/%d') if start_time else ''
        except Exception as e:
            logger.info("用户输入的时间有误:\n{}".format(e))
            start_time = end_time = ''

        if start_time and not end_time:
            news = news.filter(update_time__lte=start_time)
        if end_time and not start_time:
            news = news.filter(update_time__gte=end_time)
        if start_time and end_time:
            news = news.filter(update_time__range=(start_time, end_time))
        # 通过title进行过滤
        title = request.GET.get('title', '')
        if title:
            news = news.filter(title__icontains=title)

        # 通过作者名进行过滤
        author_name = request.GET.get('author_name', '')
        news = news.filter(author__username__icontains=author_name)

        # 通过标签id进行过滤
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.info("标签错误，\n{}".format(e))
            tag_id = 1
        news = news.filter(is_delete=False, tag_id=tag_id) or \
            news.filter(is_delete=False)

        # 获取第几页内容
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.info("当前页码数错误，\n{}".format(e))
            page = 1
        paginator = Paginator(news, constans.PER_PAGE_NEWS_COUNT)
        try:
            news_info = paginator.page(page)
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logger.info("用户访问的页数大于总页数")
            news_info = paginator.page(paginator.num_pages)

        paginator_data = paginator_script.get_paginator_data(paginator, news_info)

        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''
        context = {
            'news_info': news_info,
            'tags': tags,
            'paginator': paginator,
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'author_name': author_name,
            'tag_id': tag_id,
            'other_param': urlencode({
                "start_time": start_time,
                'end_time': end_time,
                'title': title,
                'author_name': author_name,
                'tag_id': tag_id,
            })
        }
        context.update(paginator_data)
        return render(request, 'admin/news/news_manage.html', context=context)


class NewsEditView(PermissionRequiredMixin, View):
    """
    route: /admin/news/<int>:news_id
    """
    permission_required = ('news.change_news', 'news.delete_news')
    raise_exception = True

    def handle_no_permission(self):
        return json_response(errno=Code.ROLEERR, errmsg="没有操作权限")

    def delete(self, request, news_id):
        news = News.objects.only('id').filter(id=news_id).first()
        if news:
            news.is_delete = True
            # news.save()
            news.save(update_fields=['is_delete'])
            return json_response(errmsg="文章删除成功")
        else:
            return json_response(errno=Code.PARAMERR, errmsg="需要删除的文章不存在")


class NewsPubView(PermissionRequiredMixin, View):
    """
    route: /admin/news/pub/
    """
    permission_required = ('news.add_news', 'news.view_news')
    raise_exception = True

    def get(self, request):
        tags = Tag.objects.only('id', 'name').filter(is_delete=False)

        return render(request, 'admin/news/news_pub.html', context={
            "tags": tags
        })

    def post(self, request):
        json_data = request.body
        if not json_data:
            return json_response(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_data.decode('utf8'))

        form = NewsPubForm(data=dict_data)
        if form.is_valid():
            # n = News(**form.cleaned_data)
            # n.title = form.cleaned_data.get('title')
            # 整个表单保存
            # 等插入用户信息再提交
            news_instance = form.save(commit=False)
            news_instance.author_id = request.user.id
            news_instance.save()
            return json_response(errmsg="文章创建成功！")
        else:
            # 定义一个错误信息列表
            err_msg_list = []
            for item in form.errors.values():
                err_msg_list.append(item[0])
            err_msg_str = '/'.join(err_msg_list)
            return json_response(errno=Code.PARAMERR, errmsg=err_msg_str)


class NewsUploadImage(PermissionRequiredMixin, View):

    permission_required = ('news.add_news',)

    def handle_no_permission(self):
        return json_response(errno=Code.ROLEERR, errmsg="没有操作权限")

    def post(self, request):
        image_file = request.FILES.get('image_file')
        if not image_file:
            logger.info("从前端获取图片失败")
            return json_response(errno=Code.NODATA, errmsg="长前端获取图片失败")
        if image_file.content_type not in ('images/jped', 'image/png', 'image/gif'):
            return json_response(errno=Code.DATAERR, errmsg='不能上传非图片文件')
        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.info('图片扩展名异常：{}'.format(e))
            image_ext_name = 'fpg'

        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传出现异常，{}'.format(e))
        else:
            if upload_res.get('Status') != 'Upload successed':
                logger.info('图片上传到FastDFS服务器失败')
                return json_response(errno=Code.UNKOWNERR, errmsg='图片上传到FastDFS服务器失败')
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FASTDFS_SERVER_DOMAIN + image_name
                return json_response(data={'image_url': image_url}, errmsg="图片上传成功")


def addpermission(request):
    if request.method == 'GET':
        # 获取id=1d的用户对象
        user = Users.objects.get(id=1)
        # 给该用户添加权限
        pers = Permission.objects.filter(codename__in=[
            'news.add_news',
            'news.view_news',
            'news.change_news',
            'news.delete_news',
            'tags.add_tag',
            'tags.view_tag',
            'tags.change_tag',
            'tags.delete_tag'])
        for per in pers:
            # 添加用户权限
            user.user_permissions.add(per)
            # 删除权限
            # user.user_permissions.remove(per)
        # 清空权限
        # user.user_permissions.clear()
        return HttpResponse('创建权限成功')
