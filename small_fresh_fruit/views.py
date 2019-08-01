import logging
import os
import random
from datetime import datetime
from datetime import timedelta

import itchat
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseNotFound, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django_apps.remind.models import Fruiter, WechatCode
from small_fresh_fruit.utils import query_wechat_users, register_validate

logger = logging.getLogger('app')


def register(request):
    """注册"""

    try:
        # 加载注册页面，更新微信本地库（itchat.pkl），为后续检索微信是否注册做铺垫
        # 写在这里是因为检索耗时，避免用户感觉卡顿
        try:
            itchat.get_friends(update=True)
        except KeyError as e:
            pass

        if request.method == 'GET':
            return render(request, 'register.html')
        else:
            remark_name = ''

            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            wechat_nickname = request.POST.get('wechat_nickname')
            fruit_rule = request.POST.get('fruit_rule')
            wechat_code = request.POST.get('wechat_code')

            # 后台验证注册
            if register_validate(username, password, password2, wechat_nickname, fruit_rule, wechat_code):

                # 传递过来的是remark_name(管理员的备注名)
                if 'y#' in wechat_nickname:
                    remark_name = wechat_nickname.split('y#')[-1]
                # 传递过来的是nickname
                else:
                    # 设置备注名
                    users = itchat.get_friends(update=True)
                    for user in users:
                        if user['NickName'] == wechat_nickname:
                            user_name = user['UserName']
                            remark_name = user['RemarkName']
                            if not remark_name:
                                remark_name = wechat_nickname
                                # 备注名设置为昵称
                                itchat.set_alias(user_name, remark_name)
                            break
                Fruiter.objects.create(name=username, pwd=password, wechat_remark_name=remark_name)

                # 保存到django_user
                django_user = User.objects.create_user(username=username, password=password, is_staff=True)
                django_user.save()

                # 分配权限组,可以查看提醒（确保后台新建第一个权限为提醒）
                django_user.groups.add(Group.objects.get(pk=1))

                # 注册后自动登录
                userlogin = auth.authenticate(username=username, password=password)
                auth.login(request, userlogin)
                return redirect('/admin/')
            else:
                return HttpResponse('您的浏览器版本太老，请尝试升级为主流浏览器')
    except Exception as e:
        logger.exception(e)
        return HttpResponseServerError()


def fruit_rule(request):
    """小鲜果法则~"""
    return render(request, "fruit_rule.html")


@require_POST
@csrf_exempt
def check_login_name(request):
    """检测账号是否已经注册"""
    try:
        login_name = request.POST.get('login_name')
        user = Fruiter.objects.filter(name=login_name).exists()
        if user:
            return JsonResponse({'code': 'error'})
        return JsonResponse({'code': 'ok'})
    except Exception as e:
        logger.exception(e)
        return HttpResponseServerError()


@require_POST
@csrf_exempt
def check_wechat_nickname(request):
    """检测微信昵称"""
    try:
        chat_name = request.POST.get('chat_name')

        # 备注名
        if 'y#' in chat_name:
            remark_name = chat_name.split('y#')[-1]
        else:
            # 昵称
            nick_name = chat_name
            user = itchat.search_friends(nickName=nick_name)
            if not user:
                return JsonResponse({'code': 'error'})
            elif len(user) == 1:
                remark_name = user[0]['RemarkName']
            else:
                return JsonResponse({'code': 'repeat'})

        fr = Fruiter.objects.filter(wechat_remark_name=remark_name)
        if fr:
            return JsonResponse({'code': 'conflict'})
        else:
            return JsonResponse({'code': 'ok'})
    except Exception as e:
        logger.exception(e)
        return HttpResponseServerError()


@require_POST
@csrf_exempt
def send_wechat_code(request):
    """发送微信验证码"""

    # return JsonResponse({'code': 'ok', 'wechat_code': '111111'})
    try:
        wechat_code = str(random.randint(100000, 999999))
        chat_name = request.POST.get('chat_name')

        # 验证码过期时间
        expire_time = datetime.utcnow().replace(tzinfo=utc) + timedelta(seconds=60)
        WechatCode.objects.create(wechat_name=chat_name, code=wechat_code, expire_time=expire_time)
        users = query_wechat_users(chat_name)

        msg = '【小鲜果儿提醒】\n您的验证码为{}，请在1分钟内输入'.format(wechat_code)
        user_name = users[0]['UserName']
        itchat.send(msg, toUserName=user_name)
        return JsonResponse({'code': 'ok', 'wechat_code': wechat_code})
    except Exception as e:
        logger.exception(e)
        return JsonResponse({'code': 'error'})


def get_log(request, filename):
    """远程下载日志文件"""
    try:
        if request.user.is_superuser:
            file_path = os.path.join(settings.LOG_PATH, filename)
            response = FileResponse(open(file_path, 'rb'))
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = 'attachment; filename=' + filename
            return response
        return HttpResponseForbidden()
    except Exception as e:
        logger.exception(e)
        return HttpResponseServerError()


def test_logger(request):
    room = itchat.search_friends(name='小鲜果儿')  # 这里输入你好友的名字或备注。
    print(room)
    userName = room[0]['UserName']
    f = r"D:\Download\Project\small_fresh_fruit\media\timg.png"  # 图片地址
    try:
        itchat.send_image(f, toUserName=userName)
        # 如果是其他文件可以直接send_file
        print("success")
    except:
        print("fail")
    # logger.debug('url:{}, method:{}'.format(request.path, request.method))
    return HttpResponse('logger OK!')
