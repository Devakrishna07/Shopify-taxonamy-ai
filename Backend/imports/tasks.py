import logging
from .models import ImportJob
from .services import ImportProcessor

logger = logging.getLogger(__name__)

try:
    from celery import shared_task

    @shared_task(bind=True, max_retries=1)
    def process_import_task(self, import_job_id: int):
        """
        Celery task to asynchronously process the uploaded Excel or CSV file.
        """
        try:
            import_job = ImportJob.objects.get(pk=import_job_id)
        except ImportJob.DoesNotExist:
            logger.error("ImportJob with id %s does not exist.", import_job_id)
            return

        processor = ImportProcessor()
        try:
            processor.process(import_job, import_job.file)
        except Exception as exc:
            logger.exception("Task failed for ImportJob %s: %s", import_job_id, str(exc))

except ImportError:
    # Celery not installed in environment, provide dummy wrapper
    def process_import_task(*args, **kwargs):
        pass

    class _TaskDelayShim:
        @staticmethod
        def delay(import_job_id):
            raise NotImplementedError("Celery is not installed.")

    process_import_task.delay = _TaskDelayShim.delay
