from processing.services import ProcessingService


# ...

service = ProcessingService(job)

service.start()

completed = job.completed_items
failed = job.failed_items

products = Product.objects.filter(
    status__in=[
        "PENDING",
        "FAILED",
    ]
).order_by("id")[:limit]

for product in products:

    try:

        self.stdout.write(
            f"Processing product {product.id}: "
            f"{product.title}"
        )

        result = service.process_product(product)

        if result["success"]:

            completed += 1

        else:

            failed += 1

        service.update_progress(
            completed=completed,
            failed=failed,
            last_processed_id=product.id,
        )

    except Exception as exc:

        failed += 1

        product.status = "FAILED"
        product.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        service.update_progress(
            completed=completed,
            failed=failed,
            last_processed_id=product.id,
        )

        self.stderr.write(
            self.style.ERROR(
                f"Product {product.id} failed: {exc}"
            )
        )

        # Continue processing the remaining products.
        continue

service.complete()