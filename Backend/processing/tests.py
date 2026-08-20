from unittest.mock import patch

from django.test import TestCase

from products.models import Product
from processing.models import ProcessingJob

from .batch.processor import BatchProcessor
from .batch.status import BatchStatusManager


class BatchReliabilityTests(
    TestCase
):

    def create_product(
        self,
        title,
    ):
        """
        Create a Product using the fields required
        by the current project.

        Adjust only if the Product model requires
        additional mandatory fields.
        """

        return Product.objects.create(
            title=title
        )

    # =========================================================
    # JOB CREATION
    # =========================================================

    def test_processing_job_defaults(self):

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        self.assertEqual(
            job.status,
            "PENDING",
        )

        self.assertEqual(
            job.max_retries,
            3,
        )

        self.assertEqual(
            job.retry_count,
            0,
        )

    # =========================================================
    # STATUS
    # =========================================================

    def test_status_start(self):

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        BatchStatusManager.start(
            job
        )

        job.refresh_from_db()

        self.assertEqual(
            job.status,
            "RUNNING",
        )

        self.assertIsNotNone(
            job.started_at
        )

    # =========================================================
    # SUCCESS
    # =========================================================

    @patch(
        "processing.batch.processor.ProductPipeline"
    )
    def test_successful_product(
        self,
        pipeline_mock,
    ):

        product = self.create_product(
            "Product A"
        )

        pipeline_mock.return_value.run.return_value = {
            "success": True,
            "product_id": product.id,
        }

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        result = BatchProcessor(
            job,
            chunk_size=1,
        ).run()

        job.refresh_from_db()

        self.assertEqual(
            job.status,
            "COMPLETED",
        )

        self.assertEqual(
            job.total_items,
            1,
        )

        self.assertEqual(
            job.completed_items,
            1,
        )

        self.assertEqual(
            job.failed_items,
            0,
        )

        self.assertEqual(
            result["progress"],
            100.0,
        )

    # =========================================================
    # PRODUCT FAILURE ISOLATION
    # =========================================================

    @patch(
        "processing.batch.processor.ProductPipeline"
    )
    def test_failed_product_does_not_stop_batch(
        self,
        pipeline_mock,
    ):

        product1 = self.create_product(
            "Product A"
        )

        product2 = self.create_product(
            "Product B"
        )

        def pipeline_side_effect(product):

            mock_instance = pipeline_mock.return_value

            if product.id == product1.id:

                mock_instance.run.side_effect = (
                    Exception(
                        "AI service unavailable"
                    )
                )

            else:

                mock_instance.run.side_effect = None

                mock_instance.run.return_value = {
                    "success": True,
                    "product_id": product.id,
                }

            return mock_instance

        # Use a direct processor patch instead
        # to make product-specific outcomes deterministic.
        with patch(
            "processing.batch.processor.BatchProcessor._run_pipeline"
        ) as run_pipeline:

            def side_effect(product):

                if product.id == product1.id:

                    raise Exception(
                        "AI service unavailable"
                    )

                return {
                    "success": True,
                    "product_id": product.id,
                }

            run_pipeline.side_effect = side_effect

            job = ProcessingJob.objects.create(
                job_type="FULL_PIPELINE",
                max_retries=0,
            )

            BatchProcessor(
                job,
                chunk_size=1,
            ).run()

        job.refresh_from_db()

        self.assertEqual(
            job.status,
            "COMPLETED",
        )

        self.assertEqual(
            job.completed_items,
            1,
        )

        self.assertEqual(
            job.failed_items,
            1,
        )

    # =========================================================
    # RETRY
    # =========================================================

    def test_transient_failure_is_retried(self):

        product = self.create_product(
            "Retry Product"
        )

        calls = {
            "count": 0
        }

        def pipeline(product):

            calls["count"] += 1

            if calls["count"] < 3:

                raise Exception(
                    "Temporary failure"
                )

            return {
                "success": True,
                "product_id": product.id,
            }

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE",
            max_retries=3,
        )

        with patch(
            "processing.batch.processor.BatchProcessor._run_pipeline",
            side_effect=pipeline,
        ):

            BatchProcessor(
                job,
                chunk_size=1,
            ).run()

        job.refresh_from_db()

        self.assertEqual(
            calls["count"],
            3,
        )

        self.assertEqual(
            job.retry_count,
            2,
        )

        self.assertEqual(
            job.completed_items,
            1,
        )

        self.assertEqual(
            job.failed_items,
            0,
        )

    # =========================================================
    # PERMANENT FAILURE
    # =========================================================

    def test_permanent_failure_after_retries(self):

        product = self.create_product(
            "Broken Product"
        )

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE",
            max_retries=2,
        )

        with patch(
            "processing.batch.processor.BatchProcessor._run_pipeline",
            side_effect=Exception(
                "Permanent failure"
            ),
        ):

            BatchProcessor(
                job,
                chunk_size=1,
            ).run()

        job.refresh_from_db()

        self.assertEqual(
            job.status,
            "COMPLETED",
        )

        self.assertEqual(
            job.failed_items,
            1,
        )

        self.assertEqual(
            job.completed_items,
            0,
        )

        self.assertEqual(
            job.retry_count,
            2,
        )

        self.assertIn(
            "Permanent failure",
            job.error_message,
        )

    # =========================================================
    # PROGRESS
    # =========================================================

    def test_progress_calculation(self):

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE",
            total_items=10,
            completed_items=7,
            failed_items=1,
        )

        self.assertEqual(
            BatchStatusManager.progress(
                job
            ),
            80.0,
        )

    # =========================================================
    # CHUNKING
    # =========================================================

    def test_chunking(self):

        products = []

        for index in range(5):

            products.append(
                self.create_product(
                    f"Product {index}"
                )
            )

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        processor = BatchProcessor(
            job,
            chunk_size=2,
        )

        chunks = list(
            processor._chunks(
                Product.objects.all().order_by("id"),
                2,
            )
        )

        self.assertEqual(
            len(chunks),
            3,
        )

        self.assertEqual(
            len(chunks[0]),
            2,
        )

        self.assertEqual(
            len(chunks[1]),
            2,
        )

        self.assertEqual(
            len(chunks[2]),
            1,
        )

    # =========================================================
    # LARGE BATCH SIMULATION
    # =========================================================

    def test_large_batch_simulation(self):

        Product.objects.bulk_create(
            [
                Product(
                    title=f"Product {index}"
                )
                for index in range(100)
            ]
        )

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        with patch(
            "processing.batch.processor.BatchProcessor._run_pipeline"
        ) as run_pipeline:

            run_pipeline.side_effect = (
                lambda product: {
                    "success": True,
                    "product_id": product.id,
                }
            )

            result = BatchProcessor(
                job,
                chunk_size=10,
            ).run()

        job.refresh_from_db()

        self.assertEqual(
            job.total_items,
            100,
        )

        self.assertEqual(
            job.completed_items,
            100,
        )

        self.assertEqual(
            job.failed_items,
            0,
        )

        self.assertEqual(
            job.status,
            "COMPLETED",
        )

        self.assertEqual(
            result["progress"],
            100.0,
        )

    # =========================================================
    # PIPELINE INTEGRATION
    # =========================================================

    @patch(
        "processing.batch.processor.ProductPipeline"
    )
    def test_batch_calls_existing_pipeline(
        self,
        pipeline_mock,
    ):

        product = self.create_product(
            "Pipeline Product"
        )

        pipeline_mock.return_value.run.return_value = {
            "success": True,
            "product_id": product.id,
        }

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        BatchProcessor(
            job
        ).run()

        pipeline_mock.assert_called_once_with(
            product
        )

        pipeline_mock.return_value.run.assert_called_once()

    # =========================================================
    # LAST PROCESSED PRODUCT
    # =========================================================

    @patch(
        "processing.batch.processor.BatchProcessor._run_pipeline"
    )
    def test_last_processed_id(
        self,
        run_pipeline,
    ):

        product = self.create_product(
            "Tracked Product"
        )

        run_pipeline.return_value = {
            "success": True,
            "product_id": product.id,
        }

        job = ProcessingJob.objects.create(
            job_type="FULL_PIPELINE"
        )

        BatchProcessor(
            job
        ).run()

        job.refresh_from_db()

        self.assertEqual(
            job.last_processed_id,
            product.id,
        )