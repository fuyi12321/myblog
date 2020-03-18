import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager
from utils.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(_UserManager):
    """

    """
    def create_superuser(self, username, password, email=None, **extra_fields):
        super().create_superuser(username=username, password=password, email=email, **extra_fields)


class Users(AbstractUser):
    """
    add mobile、email_active fields to Django users modules.
    """
    REQUIRED_FIELDS = ['email', 'mobile']
    objects = UserManager()
    mobile = models.CharField(max_length=11, unique=True, help_text="手机号", verbose_name="手机号", error_messages={
        "unique": "此手机号已经注册"
    })
    email_active = models.BooleanField('邮箱验证状态', default=False)

    class Meta:
        db_table = 'tb_users'      # 指定数据库表名
        verbose_name = '用户'     # 在admin站点中显示名称
        verbose_name_plural = verbose_name  # 显示复数

    def __str__(self):
        return self.username


class UserProfile(BaseModel):
    """

    """
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女')
    )
    user = models.OneToOneField('Users', on_delete=models.CASCADE, related_name='user_profile')
    nickname = models.TextField('昵称', max_length=100, null=True, blank=True, help_text='昵称')
    born_date = models.DateField('出生日期', null=True, blank=True)
    gender = models.CharField('性别', choices=GENDER_CHOICES, default='M', max_length=1)
    motto = models.TextField('个性签名', max_length=1024, null=True, blank=True)

    class Meta:
        db_table = 'tb_users_profile'
        verbose_name = '用户个人信息'
        verbose_name_plural = '用户个人信息'


@receiver(post_save, sender=Users)
def create_user_profile(sender, **kwargs):
    """
    create user profile function
    :param sender:
    :param kwargs:
    :return:
    sender
    发送post_save的参数
    模型类。
    instance
    实际实例正在保存。
    created
    一个布尔值；True如果创建了新记录。
    raw
    一个布尔值；True是否完全按照显示的方式保存模型（即在加载夹具时）。一个人不应查询/修改数据库中的其他记录，因为该数据库可能尚未处于一致状态。
    using
    正在使用的数据库别名。
    update_fields
    该组字段更新为传递给Model.save()，或者None 如果update_fields没有传递给save()。
    """
    if kwargs.get('create', False):
        # 有则改，无则建
        user_profile = UserProfile.objects.get_or_create(user=kwargs.get('instance'))
        if user_profile[-1]:
            user_profile = user_profile[0]
            user_profile.nickname = '老王'
            user_profile.born_date = datetime.date(year=1994, month=10, day=5)
            user_profile.motto = '知识就是力量'
            user_profile.save()
