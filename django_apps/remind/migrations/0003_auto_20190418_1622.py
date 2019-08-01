# Generated by Django 2.1.1 on 2019-04-18 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remind', '0002_auto_20190416_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remind',
            name='repeat',
            field=models.CharField(choices=[('no', '无'), ('weekdays', '工作日'), ('daily', '每天'), ('weekly', '每周')], default='no', max_length=10, verbose_name='周期'),
        ),
    ]