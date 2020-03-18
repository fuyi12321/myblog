from django.db import models
from utils.models import BaseModel


class Doc(BaseModel):
    """
    文件模型
    """
    file_url = models.URLField(verbose_name='文件url', help_text='文件url')
    file_name = models.CharField(verbose_name='文件名', max_length=48,  help_text='文件名')
    title = models.CharField(verbose_name='文件标题', max_length=150, help_text='文件标题')
    desc = models.TextField(verbose_name='文件描述', help_text='文件描述')
    # 不能用ImageField 要不然会存对象
    image_url = models.URLField(verbose_name='封面图片url', help_text='封面图片url', default="")
    author = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'tb_docs'        # 数据库表名
        verbose_name = '文件表'        # admin 站点中显示的名称
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
