from celery import Celery

app = Celery('tasks')
app.config_from_object('my_celery.celery_config')
