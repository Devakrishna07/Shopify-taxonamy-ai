import logging
from django.utils import timezone
from django.db import transaction

from imports.models import ImportJob, ImportRowError
from products.models import Product
from .readers import StreamingReaderFactory
from .validator import ImportValidator
from .product_creator import ProductRecordCreator

logger = logging.getLogger(__name__)


class ImportProcessor:
    """
    High-performance streaming import orchestrator.
    Processes rows in 500-item chunks, performs bulk inserts, and handles strict SKU deduplication.
    """

    BATCH_SIZE = 500

    def __init__(
        self,
        reader_factory=StreamingReaderFactory,
        validator=ImportValidator,
        record_creator=ProductRecordCreator,
    ):
        self.reader_factory = reader_factory
        self.validator = validator
        self.record_creator = record_creator

    def process(self, import_job: ImportJob, uploaded_file) -> ImportJob:
        try:
            import_job.status = "RUNNING"
            import_job.save(update_fields=["status"])

            reader = self.reader_factory.get_reader(import_job.file_name)
            processed_rows = 0
            failed_rows = 0
            total_seen = 0

            # Set of SKUs seen across this import session to catch duplicate rows within the same file
            seen_skus_in_file = set()

            for batch in reader.stream_batches(uploaded_file, batch_size=self.BATCH_SIZE):
                total_seen += len(batch)
                batch_products = []
                batch_errors = []

                # 1. Collect candidate SKUs in this batch
                batch_skus = set()
                for row_num, record in batch:
                    raw_sku = record.get("sku") or record.get("product_number") or record.get("model_number")
                    if raw_sku:
                        batch_skus.add(str(raw_sku).strip())

                # 2. Query existing SKUs in DB in a single bulk query
                existing_db_skus = set(
                    Product.objects.filter(sku__in=batch_skus).values_list("sku", flat=True)
                ) if batch_skus else set()

                # 3. Process each row in batch
                for row_num, record in batch:
                    try:
                        self.validator.validate_row_record(record)
                        raw_sku = record.get("sku") or record.get("product_number") or record.get("model_number")
                        sku_str = str(raw_sku).strip() if raw_sku else None

                        # Strict SKU Deduplication check
                        if sku_str:
                            if sku_str in existing_db_skus or sku_str in seen_skus_in_file:
                                raise ValueError(f"Duplicate SKU '{sku_str}' detected. Skipped.")
                            seen_skus_in_file.add(sku_str)

                        product_instance = self.record_creator.build_instance(record)
                        batch_products.append(product_instance)
                        processed_rows += 1

                    except Exception as err:
                        failed_rows += 1
                        batch_errors.append(
                            ImportRowError(
                                import_job=import_job,
                                row_number=row_num,
                                error_message=str(err),
                                raw_data=record,
                            )
                        )

                # 4. Atomic bulk write for this 500-item batch
                with transaction.atomic():
                    if batch_products:
                        Product.objects.bulk_create(batch_products)
                    if batch_errors:
                        ImportRowError.objects.bulk_create(batch_errors)

            # 5. Finalize counters
            import_job.total_rows = total_seen
            import_job.processed_rows = processed_rows
            import_job.failed_rows = failed_rows
            import_job.status = "COMPLETED"
            import_job.completed_at = timezone.now()
            import_job.save(
                update_fields=[
                    "total_rows",
                    "processed_rows",
                    "failed_rows",
                    "status",
                    "completed_at",
                ]
            )

            return import_job

        except Exception as exc:
            logger.exception("Import job %s encountered fatal error: %s", import_job.id, exc)
            import_job.status = "FAILED"
            import_job.completed_at = timezone.now()
            import_job.save(update_fields=["status", "completed_at"])
            raise exc
