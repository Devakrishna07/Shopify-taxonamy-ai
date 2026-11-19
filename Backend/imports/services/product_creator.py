from products.models import Product
from .normalizer import ColumnNormalizer


class ProductRecordCreator:
    """
    Builds Product model instances for bulk insertion.
    """

    @classmethod
    def build_instance(cls, record: dict) -> Product:
        title = ColumnNormalizer.string_value(record.get("title"))
        if not title:
            raise ValueError("Product title is empty.")

        product_number = ColumnNormalizer.string_value(record.get("product_number"))
        model_number = ColumnNormalizer.string_value(record.get("model_number"))
        description = ColumnNormalizer.string_value(record.get("description"))
        category = ColumnNormalizer.string_value(record.get("category"))
        subcategory = ColumnNormalizer.string_value(record.get("subcategory"))

        sku = product_number or model_number

        normalized_parts = [title, description, category, subcategory]
        normalized_text = " ".join(part for part in normalized_parts if part)

        return Product(
            external_product_id=product_number,
            sku=sku,
            title=title,
            description=description,
            brand=None,
            product_type=category,
            existing_category=category,
            existing_subcategory=subcategory,
            normalized_text=normalized_text or None,
            status="PENDING",
        )
