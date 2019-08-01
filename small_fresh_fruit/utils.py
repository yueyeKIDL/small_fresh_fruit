import logging
import os
import random
import re
from datetime import datetime

import itchat
import requests
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils.timezone import utc

from django_apps.remind.models import Fruiter, WechatCode

logger = logging.getLogger('app')


def update_weekdays_cache():
    """工作日缓存更新（每天0点）"""

    try:
        current_date = datetime.now().strftime('%Y-%m-%d')
        festival_holiday_api = "http://timor.tech/api/holiday/info/{}"
        res = requests.get(festival_holiday_api.format(current_date))
        if res.status_code == 200 and res.json()['code'] == 0:
            is_weekdays = res.json()
            # {'code': 0, 'holiday': None}
            cache.set('is_weekdays', is_weekdays)
            logger.info('工作日缓存更新时间：{} ,is_weekdays：{}'.format(datetime.now(), is_weekdays))
            return is_weekdays
        else:
            # server_code: 0服务正常, -1服务出错
            logger.warning('festival_holiday_api error, status_code:{},server_code:{}'.format(res.status_code,
                                                                                              res.json()['code']))
    except Exception as e:
        logger.exception(e)


def generate_reminder_img(title, dear, msg, content, fruiter_account):
    """生成提醒图片"""
    try:
        # 话术
        # title = '<工作日>'
        # dear = '月夜小鲜果儿凑字数凑字数凑字数'
        # msg = '一条{}的提醒！'.format(random.choice(msgr_words))
        # content = '月夜小鲜果儿凑字数技巧哦外交纠纷为为杰佛微积分辛苦破线情况我请客可千万都气我记得请我发情期觉得委屈'

        BASE_DIR = settings.BASE_DIR
        # 图片模板
        img = os.path.join(BASE_DIR, r'media\reminder\base_img\timg.png')

        # 新图片
        new_img = os.path.join(BASE_DIR, r'media\reminder\imgs\{}_{}_remind.png'.format(fruiter_account,
                                                                                        datetime.now().strftime(
                                                                                            '%Y%m%d%H%M%S')))
        # 字体
        font_type = os.path.join(BASE_DIR, r'media\reminder\fonts\small_fresh_fruit.TTF')
        font = ImageFont.truetype(font_type, 28)
        title_color = "red"
        color = "#000000"

        # 打开图片
        image = Image.open(img)
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # 位置
        title_x = 207
        title_y = width - 198

        dear_x = 166
        dear_y = width - 88

        msg_x = 142
        msg_y = width - 20

        content_x1 = 167
        content_y1 = width + 50

        content_x2 = 78
        content_y2 = width + 118

        # 写入图片
        # title
        draw.text((title_x, title_y), '%s' % title, title_color, font)

        # dear
        if len(dear) > 8:
            dear = dear[:8] + '...'
        draw.text((dear_x, dear_y), '%s' % dear, color, font)

        # msg
        draw.text((msg_x, msg_y), '%s' % msg, color, font)

        # content
        draw.text((content_x1, content_y1), '%s' % content[:10], color, font)
        draw.text((content_x2, content_y2), '%s' % content[10:23], color, font)

        # 生成图片
        image.save(new_img, 'png')
        return r'{}'.format(new_img)
    except Exception as e:
        logger.exception(e)


def close_db_connections():
    # for conn in connections.all():
    #     conn.close_if_unusable_or_obsolete()
    if connection.connection:
        connection.connection.close()
        connection.connection = None


def handle_db_connections(func):
    """装饰器-保证非request函数，exclude后数据库连接关闭，不会因数据库连接超时自动关闭"""

    def func_wrapper(*args, **kwargs):
        close_db_connections()
        result = func(*args, **kwargs)
        close_db_connections()
        return result

    return func_wrapper


def check_tomato_bell(tomato_bell_reply):
    """番茄钟格式校验"""
    # fqz 个数 分钟数 内容
    try:
        if tomato_bell_reply and 'fqz' in tomato_bell_reply:
            pattern = re.compile(r'^fqz\s+([1-9]|[1][0-9]|20)\s+([1-9]|[1-5][0-9]|60)\s+(.{0,30})$')
            match = pattern.fullmatch(tomato_bell_reply)
            if match:
                return True
    except TypeError:
        pass
    except Exception as e:
        logger.debug("tomato_bell_reply：{}".format(tomato_bell_reply))
        logger.exception(e)
    return False


def query_wechat_users(chat_name):
    """查询微信用户"""

    if 'y#' in chat_name:
        remark_name = chat_name.split('y#')[-1]
        users = itchat.search_friends(remarkName=remark_name)
    else:
        users = itchat.search_friends(nickName=chat_name)
    return users


def check_username(username):
    """用户名校验"""
    ft = Fruiter.objects.filter(name=username).exists()
    pattern = re.compile(r'[a-z0-9A-Z_]{6,16}')
    match = pattern.fullmatch(username)
    if username and not ft and match:
        return True
    return False


def check_pwd(pwd):
    """密码校验"""
    pattern = re.compile(r'.{6,16}')
    match = pattern.fullmatch(pwd)
    if pwd and match:
        return True
    return False


def check_confirm_pwd(pwd, pwd2):
    """确认密码校验"""
    if pwd == pwd2:
        return True
    return False


def check_wechat_nickname(wechat_nickname):
    """微信昵称校验"""
    users = query_wechat_users(wechat_nickname)

    # 昵称
    if len(users) == 1:
        remark_name = users[0]['RemarkName']
        fr = Fruiter.objects.filter(wechat_remark_name=remark_name)

        if wechat_nickname and not fr:
            return True
    return False


def check_fruit_rule(fruit_rule):
    """是否遵守鲜果法则校验"""
    if fruit_rule == 'on':
        return True
    return False


def check_wechat_code(chat_name, wechat_code):
    """微信验证码校验"""
    now = datetime.utcnow().replace(tzinfo=utc)
    wc = WechatCode.objects.filter(is_validate=False, wechat_name=chat_name, code=wechat_code,
                                   expire_time__gte=now).order_by('-expire_time').first()
    if wc:
        wc.is_validate = True
        wc.save()
        return True
    return False


def register_validate(username, pwd, pwd2, wechat_nickname, fruit_rule, wechat_code):
    """注册校验"""
    return check_username(username) and check_pwd(pwd) and check_confirm_pwd(pwd, pwd2) and check_wechat_nickname(
        wechat_nickname) and check_fruit_rule(fruit_rule) and check_wechat_code(wechat_nickname, wechat_code)
