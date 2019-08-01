"""small_fresh_fruit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views import static

from small_fresh_fruit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.register, name='register'),
    path('remind/', include('django_apps.remind.urls')),
    path('fruit_rule', views.fruit_rule, name='fruit_rule'),
    path('check_login_name', views.check_login_name, name='check_login_name'),
    path('check_wechat_nickname', views.check_wechat_nickname, name='check_wechat_nickname'),
    path('send_wechat_code', views.send_wechat_code, name='send_wechat_code'),
    path('get_log/<filename>', views.get_log, name='get_log'),
    path('test_logger', views.test_logger, name='test_logger'),
]
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    re_path(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}, name='media')
]
