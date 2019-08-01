from django import forms
from django.contrib import admin

from django_apps.remind.models import *

# 修改admin后台页面标题
admin.site.site_title = "小鲜果儿"
admin.site.site_header = "小鲜果儿欢迎您~"
admin.site.index_title = "快来吸果儿吧(●'◡'●)"


class TomatoBellModelForm(forms.ModelForm):
    class Meta:
        model = TomatoBell
        fields = '__all__'

    def clean_minutes(self):
        minutes = self.cleaned_data['minutes']
        if minutes > 60 or minutes < 1:
            raise forms.ValidationError('请输入合理分钟数')
        return minutes

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 1 or amount > 10:
            raise forms.ValidationError('请输入合理番茄个数，最大为10个')
        return amount


@admin.register(TomatoBell)
class TomatoBellAdmin(admin.ModelAdmin):
    form = TomatoBellModelForm

    def get_list_display(self, request):
        """用户隐藏外键字段Fruiter"""
        if request.user.is_superuser:
            self.list_display = ['tomato_name', 'amount', 'minutes', 'turn_on', 'create_time', 'fruiter']
        else:
            self.list_display = ['tomato_name', 'amount', 'minutes', 'turn_on', 'create_time']
        return self.list_display

    def get_list_filter(self, request):
        """用户隐藏过滤字段Fruiter"""
        if request.user.is_superuser:
            self.list_filter = ['minutes', 'amount', 'turn_on', 'create_time', 'fruiter']
        else:
            self.list_filter = ['minutes', 'amount', 'turn_on', 'create_time']
        return self.list_filter

    def get_form(self, request, obj=None, **kwargs):
        """对用户隐藏外键字段Fruiter"""
        if request.user.is_superuser:
            self.exclude = ()
        else:
            self.exclude = ("fruiter",)
        form = super(TomatoBellAdmin, self).get_form(request, obj, **kwargs)
        return form

    def get_queryset(self, request):
        """函数作用：使当前登录的用户只能看到自己提醒"""
        qs = super(TomatoBellAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(fruiter__name=request.user)

    def save_model(self, request, obj, form, change):
        """保存时候指定用户名"""
        if not request.user.is_superuser:
            obj.fruiter = Fruiter.objects.get(name=request.user)
        super(TomatoBellAdmin, self).save_model(request, obj, form, change)


class FruiterModelForm(forms.ModelForm):
    class Meta:
        model = Fruiter
        fields = '__all__'
        widgets = {
            'pwd': forms.PasswordInput()
        }


@admin.register(Fruiter)
class FruiterAdmin(admin.ModelAdmin):
    form = FruiterModelForm
    list_display = ('name', 'wechat_remark_name', 'is_activate', 'register_time')


@admin.register(Remind)
class RemindAdmin(admin.ModelAdmin):

    def get_list_display(self, request):
        """用户隐藏外键字段Fruiter"""
        if request.user.is_superuser:
            self.list_display = ['event', 'reminder_time', 'repeat', 'fruiter']
        else:
            self.list_display = ['event', 'reminder_time', 'repeat']
        return self.list_display

    def get_list_filter(self, request):
        """用户隐藏过滤字段Fruiter"""
        if request.user.is_superuser:
            self.list_filter = ['reminder_time', 'fruiter', 'repeat']
        else:
            self.list_filter = ['reminder_time', 'repeat']
        return self.list_filter

    def get_form(self, request, obj=None, **kwargs):
        """对用户隐藏外键字段Fruiter"""
        if request.user.is_superuser:
            self.exclude = ()
        else:
            self.exclude = ("fruiter",)
        form = super(RemindAdmin, self).get_form(request, obj, **kwargs)
        return form

    def get_queryset(self, request):
        """函数作用：使当前登录的用户只能看到自己提醒"""
        qs = super(RemindAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(fruiter__name=request.user)

    def save_model(self, request, obj, form, change):
        """保存时候指定用户名"""
        if not request.user.is_superuser:
            obj.fruiter = Fruiter.objects.get(name=request.user)
        super(RemindAdmin, self).save_model(request, obj, form, change)


@admin.register(WechatCode)
class WechatCodeAdmin(admin.ModelAdmin):
    list_display = ('wechat_name', 'code', 'expire_time', 'is_validate')
    list_filter = ['expire_time', 'is_validate']

# # Blog模型的管理器
# @admin.register(Blog)
# class BlogAdmin(admin.ModelAdmin):
#
#     def get_queryset(self, request):
#         """函数作用：使当前登录的用户只能看到自己负责的服务器"""
#         qs = super(MachineInfoAdmin, self).get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         return qs.filter(user=UserInfo.objects.filter(user_name=request.user))
#
#     # listdisplay设置要显示在列表中的字段（id字段是Django模型的默认主键）
#     list_display = ('id', 'caption', 'author', 'publish_time')
#
#     # list_per_page设置每页显示多少条记录，默认是100条
#     list_per_page = 50
#
#     # ordering设置默认排序字段，负号表示降序排序
#     ordering = ('-publish_time',)
#
#     # list_editable 设置默认可编辑字段
#     list_editable = ['machine_room_id', 'temperature']
#
#     # fk_fields 设置显示外键字段
#     fk_fields = ('machine_room_id',)
