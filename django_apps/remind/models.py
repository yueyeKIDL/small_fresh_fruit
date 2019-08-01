from django.db import models


# Create your models here.
class Fruiter(models.Model):
    name = models.CharField('用户名', max_length=30, unique=True)
    pwd = models.CharField('密码', max_length=30)
    wechat_remark_name = models.CharField('微信备注名', max_length=30)
    register_time = models.DateTimeField('注册时间', auto_now_add=True)
    is_activate = models.BooleanField('激活', default=True)

    class Meta:
        verbose_name = '鲜果儿们'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<Fruiter> - {}'.format(self.name)


remind_repeat_choices = (
    ("no", "无"),
    ("weekdays", "工作日"),
    ("daily", "每天"),
    ("weekly", "每周"),
)


class Remind(models.Model):
    fruiter = models.ForeignKey(Fruiter, on_delete=models.CASCADE)
    event = models.CharField('事件名称', max_length=23)
    reminder_time = models.DateTimeField('提醒时间')
    repeat = models.CharField('周期', max_length=10, choices=remind_repeat_choices, default='no')

    class Meta:
        verbose_name = '提醒'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<Remind> - {}'.format(self.event)


class WechatCode(models.Model):
    wechat_name = models.CharField('微信昵称', max_length=30)
    code = models.CharField('验证码', max_length=10)
    expire_time = models.DateTimeField('过期时间')
    is_validate = models.BooleanField('验证', default=False)

    class Meta:
        verbose_name = '微信验证码'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<WechatCode> - {}'.format(self.wechat_name)


class TomatoBell(models.Model):
    fruiter = models.ForeignKey(Fruiter, on_delete=models.CASCADE)
    tomato_name = models.CharField('番茄名', max_length=30)
    amount = models.IntegerField('个数')
    minutes = models.IntegerField('分钟 / 单个番茄')
    turn_on = models.BooleanField('启用', default=True)
    create_time = models.DateTimeField('创建日期', auto_now_add=True, null=True)

    class Meta:
        verbose_name = '番茄钟'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<TomatoBell> - {}'.format(self.tomato_name)

# def save(self, *args, **kwargs):
#     self.user = gen_sha1_password(self.u_login_pwd)
#     super(Remind, self).save(*args, **kwargs)

# class WechatCode(models.Model):
#     user = models.ForeignKey(Fruiter, on_delete=models.CASCADE)
#     wechat_code = models.CharField("验证码", max_length=10)
#     create_time = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
#
#     def __str__(self):
#         return self.wechat_code
#
#     class Meta:
#         # db_table = 'pro_sms_code'
#         ordering = ["-create_time"]
#         # verbose_name = _("专业版短信验证码")
#         # verbose_name_plural = verbose_name
