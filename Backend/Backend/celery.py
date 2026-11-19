import os
from celery import Celery

# Set default Django settings module for celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings")

app = Celery("Backend")

# Load configuration from Django settings, using a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
