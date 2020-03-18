import logging
import json
from django.http import HttpResponseNotFound, Http404
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F

from haystack.generic_views import SearchView
import MyBlog.settings as settings
from .models import Tag, News, Banner, HotNews, Comments
from . import constants
from utils.json_res import json_response
from utils.res_code import *

logger = logging.getLogger('django')


# Create your views here.
def index(request):
    """
    新闻首页视图
    url: /
    :param request:
    :return:
    """
    # 只取这几个
    tags = Tag.objects.only('id', 'name').filter(is_delete=False)
    # 排除这几个
    # tags = Tag.objects.defer('create_time', 'update_time', 'is_delete').filter(is_delete=False)
    hot_news = HotNews.objects.select_related('news').\
        only('news__title', 'news__image_url', 'news_id').\
        filter(is_delete=False).\
        order_by('priority', '-news__clicks')[:constants.SHOW_HOTNEWS_COUNT]
    return render(request, 'news/index.html',
                  context={
                      'tags': tags,
                      'hot_news': hot_news
                  })
    # locals() 包括所有属性
    # return render(request, 'news/base.html',
    #                   locals())


class NewsListView(View):
    """
    新闻列表视图
    url: /news/
    args: tag, page
    """
    def get(self, request):
        # 1. 判断前端传递标签分类id是否为空，是否为整数，是否超过范围
        # 2. 判断前端传递当前文章页数是否为空，是否为整数，是否超过范围
        try:
            tag_id = int(request.GET.get('tag', 0))
        except Exception as e:
            logger.error('标签错误：\n{}'.format(e))
            tag_id = 0

        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('页码错误：\n{}'.format(e))
            page = 1
        # 使用only返回的是对象，所以传递到前端时需要迭代处理
        news_queryset = News.objects.select_related('tag', 'author').only(
            'title', 'digest', 'image_url', 'update_time', 'tag__name', 'author__username')
        # values 返回字典
        # news_queryset = News.objects.values('id', 'title', 'digest', 'image_url', 'update_time'). \
        #     annotate(tag_name=F('tag__name'), author=F('author__username'))

        news = news_queryset.filter(is_delete=False, tag_id=tag_id) or \
            news_queryset.filter(is_delete=False)

        paginator = Paginator(news, constants.PER_PAGE_NEWS_COUNT)
        try:
            # 获取页面数据 get_page可以容错
            news_info = paginator.get_page(page)
        except EmptyPage:
            logging.info("用户访问的页数大于总页数")
            news_info = paginator.get_page(paginator.num_pages)
        # 序列化数据
        news_info_list = []
        for n in news_info:
            news_info_list.append({
                'id': n.id,
                'title': n.title,
                'digest': n.digest,
                'image_url': n.image_url,
                'tag_name': n.tag.name,
                'author': n.author.username,
                'update_time': n.update_time.strftime('%Y年%m月%d日 %H:%M')
            })
        data = {
            'total_pages': paginator.num_pages,
            'news': news_info_list
            # 'news': list(news_info)
        }
        return json_response(data=data)


class NewsBannerView(View):
    """
    轮播图视图
    url:/news/banners/
    """
    def get(self, request):
        # banners = Banner.objects.values('image_url', 'news_id').annotate(
        #     news_title=F('news__title')
        # ).filter(is_delete=False)[:constants.SHOW_BANNER_COUNT]
        banners = Banner.objects.select_related('news').\
                      only('image_url', 'news_id', 'news__title').\
                      filter(is_delete=False)[:constants.SHOW_BANNER_COUNT]
        # 序列化输出
        banners_info_list = []
        for b in banners:
            banners_info_list.append({
                'image_url': b.image_url,
                'news_id': b.news_id,
                'news_title': b.news.title
            })
        # 返回前端
        data = {
            'banners': banners_info_list
        }
        return json_response(data=data)


class NewDetailView(View):
    """
    新闻详情页
    route:  news/<int:news_id>/
    """
    def get(self, request, news_id):
        news = News.objects.select_related('tag', 'author').\
            only('title', 'content', 'update_time', 'tag__name', 'author__username').\
            filter(is_delete=False, id=news_id).first()
        if news:
            # 返回json需要序列化
            # 返回模版渲染不需要
            comments = Comments.objects.select_related('author', 'parent').\
                only('content', 'author__username', 'update_time',
                     'parent__author__username', 'parent__content',
                     'parent__update_time').\
                filter(is_delete=False, news_id=news_id)
            # 序列化输出
            comments_list = []
            for comm in comments:
                comments_list.append(comm.to_dict())
            return render(request, 'news/news_detail.html', context={
                'news': news,
                'comments': comments
            })
        else:
            # raise Http404("<h1>Page not found</h1>")
            return HttpResponseNotFound('<h1>Page not found</h1>')
        # 快捷方式
        # 1. 去数据库获取新闻数据
        # news_queryset = News.objects.select_related('tag', 'author').\
        # only('title', 'content', 'update_time', 'tag__name', 'author__username').\
        # filter(is_delete=False, id=news_id)
        # news = get_object_or_404(news_queryset, is_delete=False, id=news_id)

        # 2. 返回渲染页面
        # return render(request, 'news/news_detail.html', context={'news': news})


class NewsCommentView(View):
    """
    添加评论视图
    url: /news/<int:news_id>/comment/
    """
    def post(self, request, news_id):
        # 是否登录
        if not request.user.is_authenticated:
            return json_response(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])
        # 新闻是否存在
        if not News.objects.only('id').filter(is_delete=False, id=news_id).exists():
            return json_response(errno=Code.PARAMERR, errmsg='新闻不存在！')
        # 获取前端数据
        try:
            json_data = request.body
            if not json_data:
                return json_response(errno=Code.PARAMERR, errmsg="参数为空，请重新输入")
            dict_data = json.loads(json_data.decode('utf8'))
        except Exception as e:
            logger.info("错误信息，\n{}".format(e))
            return json_response(errno=Code.UNKOWNERR, errmsg=error_map[Code.UNKOWNERR])
        content = dict_data.get('content')
        # 内容是否为空
        if not content:
            return json_response(errno=Code.PARAMERR, errmsg='评论内容不能为空！')

        # 父id是否正常
        parent_id = dict_data.get('parent_id')
        if parent_id:
            try:
                # 判断是不是整数
                parent_id = int(parent_id)
                # 判断是否有父评论，父评论id是否与新闻id匹配
                if not Comments.objects.only('id').\
                        filter(is_delete=False, id=parent_id, news_id=news_id).exists():
                    return json_response(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
            except Exception as e:
                logger.info('前端传递过来的parent_id异常\n{}'.format(e))
                return json_response(errno=Code.PARAMERR, errmsg='未知异常')

        # 保存到数据库
        new_comment = Comments()
        new_comment.content = content
        new_comment.news_id = news_id
        new_comment.author = request.user
        new_comment.parent_id = parent_id if parent_id else None
        new_comment.save()

        return json_response(data=new_comment.to_dict())


class NewsSearchView(SearchView):
    """
    新闻搜索视图
    """
    # 设置搜索模板文件
    template_name = 'news/search.html'

    # 重写get请求，如果请求参数q为空，返回模型News的热门新闻数据
    # 否则根据参数q搜索相关数据
    def get(self, request, *args, **kwargs):
        # 前端输入的查询参数
        query = self.request.GET.get('q', '')
        if not query:
            # 显示热门新闻
            show_hot = True
            hot_news = HotNews.objects.select_related('news').\
                only('news__title', 'news__image_url', 'news_id').\
                filter(is_delete=False).order_by('priority', '-news__clicks')
            paginator = Paginator(hot_news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            try:
                # 页码
                page = paginator.get_page(int(self.request.GET.get('page', 1)))
            except PageNotAnInteger:
                # 如果参数page不是整数型，就返回第一页的数据
                page = paginator.get_page(1)
            except EmptyPage:
                # 用户访问的页数大于实际页数，则返回最后一页
                page = paginator.page(paginator.num_pages)

            return render(self.request, self.template_name, context={
                'page': page,
                'paginator': paginator,
                'query': query,
                'show_hot': show_hot
            })
        else:
            show_hot = False
            # 搜索
            return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """
        在context中添加page变量
        :param args:
        :param kwargs:
        :return:
        """
        context = super().get_context_data(*args, **kwargs)
        if context['page_obj']:
            context['page'] = context['page_obj']
        return context
