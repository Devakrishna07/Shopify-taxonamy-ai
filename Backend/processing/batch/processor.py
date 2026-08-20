from django.db import transaction

from products.models import Product
from processing.models import ProcessingJob
from processing.pipeline import ProductPipeline

from .status import BatchStatusManager


class BatchProcessor:
    """
    Reliable batch processor around ProductPipeline.

    Responsibilities:
        - chunk products
        - process products independently
        - retry transient failures
        - isolate permanent failures
        - update progress
        - support resume
    """

    DEFAULT_CHUNK_SIZE = 100

    def __init__(
        self,
        job,
        chunk_size=None,
    ):
        self.job = job

        self.chunk_size = (
            chunk_size
            or self.DEFAULT_CHUNK_SIZE
        )

    # =========================================================
    # PUBLIC API
    # =========================================================

    def run(self):
        """
        Execute the complete batch.

        A product failure does not terminate
        the complete batch.
        """

        BatchStatusManager.start(
            self.job
        )

        try:
            self._initialize_job()

            products = self._get_products()

            for chunk in self._chunks(
                products,
                self.chunk_size,
            ):
                self._process_chunk(chunk)

            if BatchStatusManager.is_complete(
                self.job
            ):
                BatchStatusManager.complete(
                    self.job
                )

            return self._summary()

        except Exception as exc:

            BatchStatusManager.fail(
                self.job,
                exc,
            )

            return self._summary()

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def _initialize_job(self):
        """
        Calculate total batch size.
        """

        if self.job.total_items > 0:
            return

        queryset = self._get_products()

        self.job.total_items = queryset.count()

        self.job.completed_items = 0
        self.job.failed_items = 0
        self.job.retry_count = 0

        self.job.save(
            update_fields=[
                "total_items",
                "completed_items",
                "failed_items",
                "retry_count",
                "updated_at",
            ]
        )

    # =========================================================
    # PRODUCT QUERY
    # =========================================================

    def _get_products(self):
        """
        Return products belonging to this job.

        If import_id is supplied, it is used when
        the Product model exposes a compatible
        import relationship.

        Otherwise all Products are used.
        """

        queryset = Product.objects.all()

        if not self.job.import_id:
            return queryset.order_by("id")

        # Try common import relationship names
        # without assuming one exact Product schema.
        field_names = {
            field.name
            for field in Product._meta.get_fields()
        }

        if "import_id" in field_names:
            return queryset.filter(
                import_id=self.job.import_id
            ).order_by("id")

        if "import" in field_names:
            return queryset.filter(
                import_id=self.job.import_id
            ).order_by("id")

        # Defensive fallback.
        return queryset.order_by("id")

    # =========================================================
    # CHUNKING
    # =========================================================

    @staticmethod
    def _chunks(
        queryset,
        chunk_size,
    ):
        """
        Yield product chunks without loading
        the entire queryset into memory.
        """

        batch = []

        for product in queryset.iterator(
            chunk_size=chunk_size
        ):
            batch.append(product)

            if len(batch) >= chunk_size:
                yield batch
                batch = []

        if batch:
            yield batch

    # =========================================================
    # CHUNK PROCESSING
    # =========================================================

    def _process_chunk(
        self,
        products,
    ):
        """
        Process one chunk independently.
        """

        for product in products:
            self._process_product(
                product
            )

    # =========================================================
    # PRODUCT PROCESSING
    # =========================================================

    def _process_product(
        self,
        product,
    ):
        """
        Process one product with retry handling.
        """

        attempts = 0

        while True:

            try:

                result = self._run_pipeline(
                    product
                )

                # ProductPipeline returns success=False
                # for isolated pipeline failures.
                if (
                    isinstance(result, dict)
                    and not result.get(
                        "success",
                        False,
                    )
                ):
                    raise BatchProductError(
                        result.get(
                            "error",
                            "Product pipeline failed.",
                        )
                    )

                BatchStatusManager.mark_success(
                    self.job,
                    product.id,
                )

                return result

            except Exception as exc:

                if attempts < self.job.max_retries:

                    attempts += 1

                    BatchStatusManager.increment_retry(
                        self.job
                    )

                    continue

                # Permanent failure.
                BatchStatusManager.mark_failure(
                    self.job,
                    product.id,
                    exc,
                )

                # IMPORTANT:
                # Do not raise here.
                #
                # The next product must continue.
                return {
                    "success": False,
                    "product_id": product.id,
                    "error": str(exc),
                    "status": "FAILED",
                }

    # =========================================================
    # PIPELINE
    # =========================================================

    @staticmethod
    def _run_pipeline(product):
        """
        Call the existing ProductPipeline.

        No AI or Decision logic is duplicated here.
        """

        pipeline = ProductPipeline(
            product
        )

        return pipeline.run()

    # =========================================================
    # SUMMARY
    # =========================================================

    def _summary(self):
        return {
            "job_id": self.job.id,
            "status": self.job.status,
            "total_items": self.job.total_items,
            "completed_items": (
                self.job.completed_items
            ),
            "failed_items": (
                self.job.failed_items
            ),
            "retry_count": (
                self.job.retry_count
            ),
            "progress": (
                BatchStatusManager.progress(
                    self.job
                )
            ),
            "error_message": (
                self.job.error_message
            ),
        }


class BatchProductError(Exception):
    """
    Indicates an isolated product-level failure.
    """