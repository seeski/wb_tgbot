from celery.schedules import crontab
from config_data.config import TariffInfo

def create_periodic_tasks() -> dict:
    tasks = {}
    for fr in TariffInfo.frequency:
        tasks[f'post_every_{24/fr}_hours'] = {
            'task': 'celery_config.tasks.public_posts_task',
            'schedule': crontab(minute='*/2', hour=f'*/{24/fr}'),
            'args': [fr]
        }
    return tasks