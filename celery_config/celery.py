from celery import Celery
from services.services import create_periodic_tasks

app = Celery('celery_config',
             broker='redis://localhost:6379',
             backend='redis://localhost:6379',
             include=['celery_config.tasks'])

# Optional configuration, see the application user guide.
app.conf.enable_utc = False
app.conf.update(result_expires=3600)
app.conf.update(timezone='Europe/Moscow')

app.conf.beat_schedule = create_periodic_tasks()


app.autodiscover_tasks()


if __name__ == '__main__':
    app.start()