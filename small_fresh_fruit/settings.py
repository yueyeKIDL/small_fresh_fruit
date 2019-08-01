"""
Django settings for small_fresh_fruit project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

SMALL_FRESH_FRUIT_DEBUG = False

# 微信管理员昵称
# ADMIN_WECHAT_NICKNAME = '小鲜果儿'
# ADMIN_WECHAT_NICKNAME = '月夜yueyeKIDL'
# ADMIN_WECHAT_NICKNAME = '火力全开'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加apps路径
sys.path.insert(0, os.path.join(BASE_DIR, 'django_apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vx%e&$20^c*t92wwur$$2ygds43r9lnr!k=1$5^f)=vj_ydz%!'

# SECURITY WARNING: don't run with debug turned on in production!
if SMALL_FRESH_FRUIT_DEBUG:
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['mengmeng.pythonanywhere.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_apps.remind',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'small_fresh_fruit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'small_fresh_fruit.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if SMALL_FRESH_FRUIT_DEBUG:
    # 本地服务器
    PASSWORD = 'root'
else:
    # 生产服务器
    PASSWORD = 'rootroot'

DATABASES = {
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'my_django',
        'USER': 'root',
        'PASSWORD': PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',  # 数据库缓存
        'LOCATION': 'my_cache_table',  # 缓存数据表
        'TIMEOUT': 24 * 60 * 60,  # 缓存超时时间（默认300，None表示永不过期）
        'OPTIONS': {
            'MAX_ENTRIES': 365,  # 最大缓存个数（默认300）
            'CULL_FREQUENCY': 3,  # 缓存到达最大个数之后，剔除缓存个数的比例，即：1/CULL_FREQUENCY（默认3）
        },
    }

}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

# 页面显示该时区时间
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

# 控制入库时间是否UTC
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")

# 这个是设置静态文件夹目录的路径
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# 设置文件上传路径，图片上传、文件上传都会存放在此目录里
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 日志路径
LOG_PATH = os.path.join(BASE_DIR, 'log')

# 如果地址不存在，则自动创建log文件夹
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# 日志系统
LOGGING = {
    # version只能为1,定义了配置文件的版本，当前版本号为1.0
    "version": 1,
    # True表示禁用logger
    "disable_existing_loggers": False,
    # 格式化
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s [%(filename)s -> def %(funcName)s:line %(lineno)d] [%(message)s]'
        },
        'stander': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s%(funcName)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]'
        },
        'simple': {
            'format': '%(levelno)s %(module)s %(asctime)s %(message)s'
        }
    },

    'handlers': {
        'app_handlers': {
            'level': 'DEBUG',
            # 超过5M重新命名，然后写入新的日志文件 txt.1,txt.2 ...
            'class': 'logging.handlers.RotatingFileHandler',
            # 指定文件大小
            'maxBytes': 5 * 1024 * 1024,
            # 文件数
            'backupCount': 5,
            # 指定文件地址
            'filename': '%s/app.log' % LOG_PATH,
            # 格式
            'formatter': 'default',
            # 编码
            'encoding': 'utf-8',
        },
        # 'uauth_handlers': {
        #     'level': 'DEBUG',
        #     # 超过5M重新命名，然后写入新的日志文件 txt.1,txt.2 ...
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     # 指定文件大小
        #     'maxBytes': 5 * 1024 * 1024,
        #     # 文件数
        #     'backupCount': 5,
        #     # 指定文件地址
        #     'filename': '%s/uauth.txt' % LOG_PATH,
        #     # 格式
        #     'formatter': 'default',
        #     # 编码
        #     'encoding': 'utf-8',
        # }
    },

    'loggers': {
        'app': {
            'handlers': ['app_handlers'],
            'level': 'DEBUG'
        },
        # 'auth': {
        #     'handlers': ['uauth_handlers'],
        #     'level': 'INFO'
        # }
    },

    'filters': {

    }
}