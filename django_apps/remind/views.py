import hashlib
import logging
import os
import random
import threading
import time
from datetime import datetime
from datetime import timedelta

import requests
from apscheduler.schedulers import SchedulerNotRunningError
from django.db import connection
import itchat
import pytz
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from django_apps.remind.models import *
from small_fresh_fruit.utils import check_tomato_bell, handle_db_connections, generate_reminder_img, \
    update_weekdays_cache

logger = logging.getLogger('app')

solar_words = ['自谦', '隐忍', '奉公', '刻苦', '威武', '自尊', '温和', '仗义', '超伦', '认真', '宽容', '老练', '雍容', '强壮', '助人', '勇敢', '坚韧',
               '可爱', '好学', '灵巧', '仁人', '诚恳', '优雅', '友善', '德劭', '活泼', '厚德', '勤恳', '老实', '拼搏', '顽强', '踏实', '谨慎', '能干',
               '德厚', '忠诚', '律己', '机灵', '细腻', '幽默', '体贴', '团结', '钻研', '宽宏', '主动', '专注', '杰出', '忠心', '坚强', '高大', '高尚',
               '好施', '端庄', '德高', '自觉', '志士', '毅然', '教养', '实际', '负重', '勤奋', '聪明', '热情', '真诚', '豁达', '虚心', '磊落', '舍己',
               '忠贞', '大度', '壮志', '直率', '可靠', '雄心', '自强', '天真', '尊贵', '蕙心', '决然', '廉洁', '光明', '客观', '阳光', '奉献', '勤劳',
               '直爽', '刚正', '沉稳', '克己', '干练', '友爱', '自爱', '谦虚', '乐观', '亲爱']

msg_words = ['独树一帜', '戴月披星', '持之以恒', '斗志昂扬', '精诚团结', '见贤思齐', '自强不息', '不屈不挠', '别具匠心', '力争上游', '标新立异', '壮志凌云', '奋发图强',
             '坚持不懈', '坚定不移', '发奋图强', '百折不挠', '英勇无畏', '人定胜天', '一往无前', '知耻而后勇', '一日千里', '只争朝夕', '坚忍不拔', '朝气蓬勃', '铁杵成针',
             '百尺竿头', '锲而不舍', '苦心孤诣', '百尺竿头', '更进一步', '革故鼎新', '发愤忘食', '坚如磐石', '别具一格', '悬梁刺股', '坚持不懈', '革放鼎新', '水滴石穿',
             '不知寝食', '更进一步', '大智大勇', '不耻下问', '继往开来', '毛遂自荐', '积极进取', '矢志不移', '不甘示弱', '洗心革面', '奋不顾身', '坚毅顽强', '改天换地',
             '滴水穿石', '勇往直前', '推陈出新', '励精图治', '追根问底', '万象更新', '不甘后人', '囊萤映雪', '齐心协力', '精益求精', '兢兢业业']

remind_repeat_mapping = {
    "no": "<一次性>",
    "weekdays": "<工作日>",
    "daily": "<每 日>",
    "weekly": "<每 周>",
}

# 自动回复网址
reply_url = ['1', '主页']


@csrf_exempt
def session_login(request):
    if request.method == "GET":
        request.session['username'] = '666'
        request.session['is_login'] = True
        # request.session.set_expiry(10)
        return HttpResponse('save session')


def get_session(request):
    if request.method == "GET":
        res = request.session.get('username'), request.session.get('is_login')
        return HttpResponse(res)


# Create your views here.


def wechat_admin_login(request):
    if request.user.is_superuser:
        itchat.auto_login(hotReload=True)  # 首次扫描登录后后续自动登录
        return HttpResponse('小鲜果儿回来了~')
    return HttpResponseForbidden()


@csrf_exempt
def check_file_size(request):
    """校验文件大小"""

    s = b''
    # s = bytearray()
    file = request.FILES.get('jk')
    for chunk in file.chunks():
        print(type(chunk))
        s += chunk
    md5Obj1 = hashlib.md5()
    md5Obj1.update(s)
    print(1111, md5Obj1.hexdigest())
    md5Obj = hashlib.md5()
    for chunk in file.chunks():
        md5Obj.update(chunk)
    print(md5Obj.hexdigest() == md5Obj1.hexdigest())
    return HttpResponse('ok')


def into_db(request):
    """批量添加数据（测试用）"""
    try:
        reminder_time = datetime.now()
        user = Fruiter.objects.get(name='15620955564')
        for i in range(5):
            reminder_time += timedelta(minutes=1)
            data = {
                'user': user,
                'event': '事件%s' % i,
                'reminder_time': reminder_time,
            }
            Remind.objects.create(**data)
        return HttpResponse('5条提醒入库成功')
    except Exception as e:
        logger.exception(e)
        return HttpResponseServerError()


def send_wechat_tomato_bell(tomato_bell_no, amount, tomato_name, msg):
    """发送番茄钟提醒"""
    try:
        itchat.send('【番茄钟{}/{}】\n内容为：{}'.format(tomato_bell_no, amount, tomato_name), toUserName=msg['FromUserName'])
        if tomato_bell_no == amount:
            # 番茄钟关闭
            time.sleep(0.3)
            itchat.send('恭喜您已完成所有番茄钟！', toUserName=msg['FromUserName'])
            fruiter = Fruiter.objects.filter(wechat_remark_name=msg['User']['RemarkName']).first()
            tmb = TomatoBell.objects.filter(fruiter=fruiter, turn_on=True).first()
            if tmb:
                tmb.turn_on = False
                tmb.save()
    except Exception as e:
        logger.exception(e)


def send_img_remind(remind_object):
    """发送图片提醒"""

    try:
        # 使用备注名来查找实际用户名
        db_wechat_name = remind_object.fruiter.wechat_remark_name
        fruiter_account = remind_object.fruiter.name
        users = itchat.search_friends(remarkName=db_wechat_name)

        # 针对微信限定，管理员无备注名的问题
        if not users:
            users = itchat.search_friends(name=db_wechat_name)
        user_name = users[0]['UserName']

        # 缓存
        users = cache.get('wechat_users')
        if not users:
            users = itchat.get_friends(update=True)
            cache.set('wechat_users', users)

        for user in users:
            if user['RemarkName'] == db_wechat_name:
                nick_name = user['NickName']
                break
        else:
            nick_name = db_wechat_name

        repeat_type = remind_object.repeat
        title = remind_repeat_mapping[repeat_type]
        msg = '一条{}的提醒！'.format(random.choice(msg_words))
        reminder_img_path = generate_reminder_img(title, nick_name, msg, remind_object.event, fruiter_account)
        itchat.send_image(reminder_img_path, toUserName=user_name)
    except Exception as e:
        logger.exception(e)


def send_wechat_remind(remind_object):
    """发送微信文字提醒"""
    try:
        # 使用备注名来查找实际用户名
        db_wechat_name = remind_object.fruiter.wechat_remark_name
        users = itchat.search_friends(remarkName=db_wechat_name)

        # 针对微信限定，管理员无备注名的问题
        if not users:
            users = itchat.search_friends(name=db_wechat_name)
        user_name = users[0]['UserName']
        reminder_time = remind_object.reminder_time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(
            '%Y-%m-%d %H:%M')

        # 缓存
        users = cache.get('wechat_users')
        if not users:
            users = itchat.get_friends(update=True)
            cache.set('wechat_users', users)

        for user in users:
            if user['RemarkName'] == db_wechat_name:
                nick_name = user['NickName']
                break
        else:
            nick_name = db_wechat_name

        solar_word = random.choice(solar_words)
        repeat_type = remind_object.repeat

        itchat.send(
            '【小鲜果儿{}提醒】\n{}的 "{}"，您有一条提醒！\n内容为：{}'.format(remind_repeat_mapping[repeat_type], solar_word, nick_name,
                                                          remind_object.event),
            toUserName=user_name)
        # print('{} -- it is {}'.format(remind_object.event, reminder_time))
    except Exception as e:
        logger.exception(e)


def search_and_send_weekdays_img(now):
    """查询工作日提醒，并发送提醒图片"""
    res = Remind.objects.filter(repeat='weekdays')
    for re in res:
        if re.reminder_time.strftime('%H:%M') == now.strftime('%H:%M'):
            time.sleep(0.2)
            # send_wechat_remind(remind_object=re)
            send_img_remind(remind_object=re)


def send_weekdays_remind(now):
    """发送工作日提醒"""

    try:
        # 查询缓存工作日
        is_weekdays = cache.get('is_weekdays')
        # 设置缓存
        if not is_weekdays:
            is_weekdays = update_weekdays_cache()
        # 判断是否工作日
        '''{
              "code": 0,              // 0服务正常。-1服务出错
              "holiday": {
                "holiday": false,     // true表示是节假日，false表示是调休
                "name": "国庆前调休",  // 节假日的中文名。如果是调休，则是调休的中文名，例如'国庆前调休'
                "wage": 1,            // 薪资倍数，1表示是1倍工资
                "after": false,       // 只在调休下有该字段。true表示放完假后调休，false表示先调休再放假
                "target": '国庆节'     // 只在调休下有该字段。表示调休的节假日
              }
            }'''
        current_date = datetime.now()
        if is_weekdays['holiday'] is None:
            if current_date.isoweekday() not in [6, 7]:
                search_and_send_weekdays_img(now)
        elif is_weekdays['holiday']['holiday'] is False:
            search_and_send_weekdays_img(now)
    except Exception as e:
        logger.exception(e)


def send_common_remind(now_format_zero_seconds):
    """发送普通提醒"""
    try:
        res = Remind.objects.filter(repeat='no', reminder_time__range=[now_format_zero_seconds,
                                                                       now_format_zero_seconds + timedelta(seconds=59)])
        if res:
            for re in res:
                time.sleep(0.2)
                # send_wechat_remind(remind_object=re)
                send_img_remind(remind_object=re)
    except Exception as e:
        logger.exception(e)


def send_daily_remind(now):
    """发送每日提醒"""
    try:
        res = Remind.objects.filter(repeat='daily')
        if res:
            for re in res:
                if re.reminder_time.strftime('%H:%M') == now.strftime('%H:%M'):
                    time.sleep(0.2)
                    # send_wechat_remind(remind_object=re)
                    send_img_remind(remind_object=re)
    except Exception as e:
        logger.exception(e)


def send_weekly_remind(now):
    """发送每周提醒"""
    try:
        res = Remind.objects.filter(repeat='weekly')
        if res:
            for re in res:
                db_reminder_time = re.reminder_time
                if db_reminder_time.isoweekday() == now.isoweekday() and db_reminder_time.strftime(
                        '%H:%M') == now.strftime('%H:%M'):
                    time.sleep(0.2)
                    # send_wechat_remind(remind_object=re)
                    send_img_remind(remind_object=re)
    except Exception as e:
        logger.exception(e)


def search_db():
    """查询用户提醒数据（轮询事件）"""
    try:
        now = datetime.utcnow().replace(tzinfo=utc)
        now_format_zero_seconds = now.replace(second=0, microsecond=0)
        # print('搜寻已到时间的提醒事件...', now.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%Y-%m-%d %H:%M'))

        t1 = threading.Thread(target=send_common_remind, args=(now_format_zero_seconds,))
        t2 = threading.Thread(target=send_daily_remind, args=(now,))
        t3 = threading.Thread(target=send_weekly_remind, args=(now,))
        t4 = threading.Thread(target=send_weekdays_remind, args=(now,))

        t1.start()
        # 修正同时间发送提醒，消息被吞
        time.sleep(0.5)
        t2.start()
        time.sleep(0.5)
        t3.start()
        time.sleep(0.5)
        t4.start()
    except Exception as e:
        logger.exception(e)


# 查询全部好友信息
# friends = itchat.get_friends(update=True)
# print(friends)

scheduler_tomato_bell = BackgroundScheduler()


# 微信自动回复
@itchat.msg_register(itchat.content.INCOME_MSG)
@handle_db_connections
def tomato_bell_reply(msg):
    try:
        if msg['Text'] in reply_url:
            return "【欢迎访问小鲜果儿~】\n主页：\nhttp://liguo.zzl99.cn:8000/admin/remind/remind/" \
                   "\n去注册：\nhttp://liguo.zzl99.cn:8000/"
        elif check_tomato_bell(msg['Text']):
            # 定时番茄钟
            # fqz 个数 分钟数 提醒内容

            fruiter = Fruiter.objects.filter(wechat_remark_name=msg['User']['RemarkName']).first()
            if not fruiter:
                return '请先注册小鲜果儿账号，点这里：http://liguo.zzl99.cn:8000/'

            tmb = TomatoBell.objects.filter(fruiter=fruiter, turn_on=True).first()
            if tmb:
                return '已创建番茄钟，请集中精力完成，切不可贪心哦~'
            else:
                _, amount, minutes, *tomato_name = msg['Text'].split()
                tomato_name = ' '.join(tomato_name)
                amount, minutes = int(amount), int(minutes)
                data = dict(fruiter=fruiter, amount=amount, minutes=minutes, tomato_name=tomato_name, turn_on=True)
                TomatoBell.objects.create(**data)

            global scheduler_tomato_bell
            scheduler_tomato_bell = BackgroundScheduler()

            run_date = (datetime.now() + timedelta(minutes=minutes)).replace(microsecond=0)
            # run_date = (datetime.now() + timedelta(seconds=minutes)).replace(microsecond=0)
            for i in range(amount):
                # 在指定的时间，只执行一次
                tomato_bell_no = i + 1
                scheduler_tomato_bell.add_job(send_wechat_tomato_bell, 'date',
                                              run_date=run_date,
                                              args=[tomato_bell_no, amount, tomato_name, msg, ],
                                              id=msg['User']['RemarkName'] + str(tomato_bell_no))
                run_date += timedelta(minutes=minutes)
                # run_date += timedelta(seconds=minutes)
            scheduler_tomato_bell.start()
            return '您的番茄钟已设定成功'
        elif msg['Text'] in ['fq', 'fqz', '番茄钟']:
            # 番茄钟格式说明
            return '【番茄钟格式】\nfqz <个数> <分钟数> <提醒内容>\n如：设定3个番茄钟，每个10分钟\n例：fqz 3 10 我是番茄钟~（空格间隔）\n取消番茄钟：qxfqz'
        elif msg['Text'] in ['qxfqz']:
            fruiter = Fruiter.objects.filter(wechat_remark_name=msg['User']['RemarkName']).first()
            if not fruiter:
                return '请先注册小鲜果儿账号，点这里：http://liguo.zzl99.cn:8000/'
            tmb = TomatoBell.objects.filter(fruiter=fruiter, turn_on=True).first()
            if not tmb:
                return '您还没有设定番茄钟'
            tmb.turn_on = False
            tmb.save()
            try:
                scheduler_tomato_bell.shutdown()
            except SchedulerNotRunningError:
                pass
            return '您的番茄钟已删除'
    except Exception as e:
        logger.exception(e)


itchat.auto_login(hotReload=True)
itchat.run(blockThread=False)

current_second = datetime.utcnow().replace(tzinfo=utc).second
# 当前分5秒内，立即检索库中提醒事件
if current_second in range(6):
    search_db()
# 至整分时间，检索库
else:
    adjust_seconds = 61 - current_second
    print('正在调成至整分，请稍等{}s...'.format(adjust_seconds))
    time.sleep(adjust_seconds)
    search_db()

# 非阻塞轮询

scheduler_search_db = BackgroundScheduler()
scheduler_search_db.add_job(search_db, 'interval', seconds=60)
scheduler_search_db.add_job(update_weekdays_cache, "cron", day_of_week='*', hour='0', minute='0')
scheduler_search_db.start()
