from celery import Celery

app = Celery(
    'auto_alpha_miner',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['auto_alpha_miner.tasks']
)

app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3000, # 50 minutes
)

if __name__ == '__main__':
    app.start()
