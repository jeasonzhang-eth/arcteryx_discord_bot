from __future__ import absolute_import
from celery.schedules import crontab
from datetime import timedelta

# 使用redis存储任务队列
broker_url = 'redis://:Jeason52@127.0.0.1:16379/0'
# 使用redis存储结果
result_backend = 'redis://:Jeason52@127.0.0.1:16379/0'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
# 时区设置
timezone = 'Asia/Shanghai'
# celery默认开启自己的日志
# False表示不关闭
worker_hijack_root_logger = False
# 存储结果过期时间，过期后自动删除
# 单位为秒
result_expires = 60 * 60 * 24

# 导入任务所在文件
imports = [
    'my_celery.tasks',
]

# 需要执行任务的配置
beat_schedule = {
    'test1': {
        # 具体需要执行的函数
        # 该函数必须要使用@app.task装饰
        'task': 'my_celery.tasks.update_commodity',
        # 定时时间
        # 每分钟执行一次，不能为小数
        'schedule': crontab(minute='*/1'),
        # 或者这么写，每小时执行一次
        # "schedule": crontab(minute=0, hour="*/1")
        # 执行的函数需要的参数
        'args': ()
    },
    'test2': {
        'task': 'my_celery.tasks.crawl_monitor',
        # 设置定时的时间，10秒一次
        'schedule': timedelta(seconds=10),
        'args': ()
    }
}