from celery import Celery
from services.services import create_periodic_tasks

app = Celery('celery_config',
             broker='redis://redis:6380',
             backend='redis://redis:6380',
             include=['celery_config.tasks'])

# Optional configuration, see the application user guide.
app.conf.enable_utc = False
app.conf.update(result_expires=3600)
app.conf.update(timezone='Europe/Moscow')

app.conf.beat_schedule = create_periodic_tasks()


app.autodiscover_tasks()


if __name__ == '__main__':
    app.start()