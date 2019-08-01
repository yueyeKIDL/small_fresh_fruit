# small fresh fruit #


![Travis](https://img.shields.io/badge/language-python+django-green?style=flat-square&logo=appveyor.)
## 通过与微信交互，设置番茄钟和常用提醒 ##
#### 准备工作：
1. 创建管理员 python manage.py createsuperuser
2. 创建缓存表 python manage.py createcachetable
3. 迁移 python manage.py migrate
4. 后台创建组权限 -> remind-提醒

#### 使用说明：

> 与微信交互进行操作

1. 回复'1' 或者 '主页'，显示注册和提醒设置传送门
2. 回复'fq'、'fqz' 或者 '番茄钟'，显示番茄钟操作指南

