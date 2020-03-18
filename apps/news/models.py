from django.db import models
from django.core.validators import MinLengthValidator
from utils.models import BaseModel


class Tag(BaseModel):
    """
    文章分类标签模型
    """
    name = models.CharField('标签名', max_length=64, help_text='标签名')

    class Meta:
        ordering = ['-update_time', '-id']      # 排序
        db_table = "tb_tag"                     # 指明数据库表名
        verbose_name = "文章标签"                # 在admin站点中显示的名称
        verbose_name_plural = verbose_name      # 显示的复数名称

    def __str__(self):
        return self.name


class News(BaseModel):
    """
    文章模型
    """
    title = models.CharField('标题', max_length=150, validators=[MinLengthValidator(1), ], help_text='标题')
    digest = models.CharField('摘要', max_length=200, validators=[MinLengthValidator(1), ], help_text='摘要')
    content = models.TextField('内容', help_text='内容')
    clicks = models.IntegerField('点击量', default=0, help_text='点击量')
    image_url = models.URLField('图片url', default='', help_text='图片url')
    # 一对多 外键在多的这一个键，一为主表，多为子表
    # CASCADE   级联，主表一删除，子表也删除
    # PROTECT   主表一删，子表报错
    # SET_NULL  主表一删，子表相对应数据设置为null，同时设置null=True
    # SET_DEFAULT   主表一删，子表相对应数据设置为默认值，同时设置default=xx,
    # SET   # 指定一个可调用对象，函数返回的值赋给子表
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-update_time', '-id']  # 排序
        db_table = "tb_news"  # 指明数据库表名
        verbose_name = "新闻"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.title


class Comments(BaseModel):
    """
    评论模型
    """
    content = models.TextField('内容', help_text='内容')
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)
    news = models.ForeignKey('News', on_delete=models.CASCADE)
    # 本项目设计二级评论，修改Comments模型，添加一个parent字段
    # null 是针对数据库而言，如果 null=True, 表示数据库的该字段可以为空，那么在新建一个model对象的时候是不会报错的！！
    # blank 是针对表单的，如果 blank=True，表示你的表单填写该字段的时候可以不填，比如 admin 界面下增加 model 一条记录的时候。直观的看到就是该字段不是粗体。
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-update_time', '-id']  # 排序
        db_table = "tb_comments"  # 指明数据库表名
        verbose_name = "评论"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def to_dict(self):
        comment_dict = {
            'news_id': self.news.id,
            'comment_id': self.id,
            'content': self.content,
            'author': self.author.username,
            'update_time': self.update_time.strftime('%Y年%m月%d日 %H:%M'),
            'parent': self.parent.to_dict() if self.parent else None,
        }
        return comment_dict

    def __str__(self):
        return '<评论{}>'.format(self.id)


class HotNews(BaseModel):
    """
    推荐文章表
    """
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级')
    ]
    news = models.OneToOneField('News', on_delete=models.CASCADE)
    priority = models.IntegerField(verbose_name='优先级', help_text='优先级', choices=PRI_CHOICES, default=3)

    class Meta:
        ordering = ['priority', '-update_time', '-id']  # 排序
        db_table = "tb_hotnews"  # 指明数据库表名
        verbose_name = "热门新闻"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<热门新闻{}>'.format(self.id)


class Banner(BaseModel):
    """
    轮播图
    """
    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
        (4, '第四级'),
        (5, '第五级'),
        (6, '第六级'),
    ]
    image_url = models.URLField(verbose_name='轮播图url', help_text='轮播图url')
    priority = models.IntegerField(verbose_name='优先级', help_text='优先级', choices=PRI_CHOICES, default=6)

    news = models.OneToOneField('News', on_delete=models.CASCADE)

    class Meta:
        ordering = ['priority', '-update_time', '-id']  # 排序
        db_table = "tb_banner"  # 指明数据库表名
        verbose_name = "轮播图"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '<轮播图{}>'.format(self.id)
