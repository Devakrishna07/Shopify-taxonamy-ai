import csv
import io

import pandas as pd

from django.db import transaction
from django.utils import timezone

from .models import ImportJob, ImportRowError
from products.models import Product


# ============================================================
# COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {
    "product name": "title",
    "product_name": "title",
    "productname": "title",
    "title": "title",

    "product number": "product_number",
    "product_number": "product_number",
    "sku": "product_number",

    "model number": "model_number",
    "model_number": "model_number",

    "product category": "category",
    "product_category": "category",

    "product sub category": "subcategory",
    "product sub category ": "subcategory",
    "product_sub_category": "subcategory",

    "product description": "description",
    "product description ": "description",
    "product_description": "description",

    "product color": "product_color",
    "product_color": "product_color",

    "color collection": "color_collection",
    "color_collection": "color_collection",

    "collection name": "collection_name",
    "collection_name": "collection_name",

    "materials": "materials",
    "material": "materials",

    "product dimensions": "dimensions",
    "product dimensions ": "dimensions",
    "product_dimensions": "dimensions",

    "product url": "product_url",
    "product_url": "product_url",
}


# ============================================================
# HELPERS
# ============================================================

def normalize_column_name(column):
    """
    Normalize an Excel/CSV column name.

    Example:
        Product Name -> product name
        Product Description  -> product description
    """

    if column is None:
        return ""

    return str(column).strip().lower()


def normalize_dataframe_columns(dataframe):
    """
    Convert external spreadsheet column names into
    internal names used by the import pipeline.
    """

    rename_map = {}

    for column in dataframe.columns:

        normalized = normalize_column_name(column)

        if normalized in COLUMN_ALIASES:
            rename_map[column] = COLUMN_ALIASES[normalized]

    dataframe = dataframe.rename(
        columns=rename_map
    )

    return dataframe


def clean_value(value):
    """
    Convert pandas values into database-friendly values.
    """

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


def dataframe_to_records(dataframe):
    """
    Convert dataframe rows to dictionaries.
    """

    records = []

    for _, row in dataframe.iterrows():

        record = {}

        for column, value in row.items():
            record[column] = clean_value(value)

        records.append(record)

    return records


def string_value(value):
    """
    Safely convert a value into a trimmed string.

    Returns None for empty values.
    """

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


# ============================================================
# FILE READER
# ============================================================

def read_import_file(uploaded_file):
    """
    Read XLSX or CSV uploaded through Django REST Framework.
    """

    filename = uploaded_file.name.lower()

    # --------------------------------------------------------
    # XLSX
    # --------------------------------------------------------

    if filename.endswith(".xlsx"):

        dataframe = pd.read_excel(
            uploaded_file,
            engine="openpyxl"
        )

        return dataframe

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    if filename.endswith(".csv"):

        dataframe = pd.read_csv(
            uploaded_file
        )

        return dataframe

    raise ValueError(
        "Only CSV and XLSX files are supported."
    )


# ============================================================
# VALIDATE COLUMNS
# ============================================================

def validate_required_columns(dataframe):
    """
    Validate the normalized dataframe.

    The import pipeline requires a product title.
    """

    required_columns = [
        "title",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# ============================================================
# CREATE PRODUCT
# ============================================================

def create_product_from_record(record):
    """
    Create a Product database record from one
    normalized import record.

    The Product model currently supports:

        external_product_id
        sku
        title
        description
        brand
        product_type
        existing_category
        existing_subcategory
        normalized_text
        status
    """

    title = string_value(
        record.get("title")
    )

    if not title:
        raise ValueError(
            "Product title is empty."
        )

    product_number = string_value(
        record.get("product_number")
    )

    model_number = string_value(
        record.get("model_number")
    )

    description = string_value(
        record.get("description")
    )

    category = string_value(
        record.get("category")
    )

    subcategory = string_value(
        record.get("subcategory")
    )

    # --------------------------------------------------------
    # Determine SKU
    # --------------------------------------------------------
    #
    # Prefer Product Number.
    # If Product Number is unavailable,
    # use Model Number.
    #

    sku = product_number or model_number

    # --------------------------------------------------------
    # Build normalized text
    # --------------------------------------------------------

    normalized_parts = [
        title,
        description,
        category,
        subcategory,
    ]

    normalized_text = " ".join(
        value
        for value in normalized_parts
        if value
    )

    # --------------------------------------------------------
    # Create Product
    # --------------------------------------------------------

    product = Product.objects.create(
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

    return product


# ============================================================
# PROCESS IMPORT
# ============================================================

def process_import(import_job, uploaded_file):
    """
    Main import processor.

    Responsibilities:

    1. Read CSV/XLSX
    2. Normalize column names
    3. Validate required fields
    4. Create Product records
    5. Count rows
    6. Track row-level errors
    7. Update ImportJob status
    """

    try:

        # ----------------------------------------------------
        # Mark job as running
        # ----------------------------------------------------

        import_job.status = "RUNNING"

        import_job.save(
            update_fields=["status"]
        )

        # ----------------------------------------------------
        # Read file
        # ----------------------------------------------------

        dataframe = read_import_file(
            uploaded_file
        )

        # ----------------------------------------------------
        # Remove completely empty rows
        # ----------------------------------------------------

        dataframe = dataframe.dropna(
            how="all"
        )

        # ----------------------------------------------------
        # Normalize column names
        # ----------------------------------------------------

        dataframe = normalize_dataframe_columns(
            dataframe
        )

        # ----------------------------------------------------
        # Validate required columns
        # ----------------------------------------------------

        validate_required_columns(
            dataframe
        )

        # ----------------------------------------------------
        # Total rows
        # ----------------------------------------------------

        total_rows = len(dataframe)

        import_job.total_rows = total_rows
        import_job.processed_rows = 0
        import_job.failed_rows = 0

        import_job.save(
            update_fields=[
                "total_rows",
                "processed_rows",
                "failed_rows",
            ]
        )

        # ----------------------------------------------------
        # Process individual rows
        # ----------------------------------------------------

        processed_rows = 0
        failed_rows = 0

        records = dataframe_to_records(
            dataframe
        )

        for index, record in enumerate(
            records,
            start=2
        ):

            try:

                # ------------------------------------------------
                # Validate title
                # ------------------------------------------------

                title = record.get("title")

                if (
                    title is None
                    or str(title).strip() == ""
                ):

                    raise ValueError(
                        "Product title is empty."
                    )

                # ------------------------------------------------
                # Create Product
                # ------------------------------------------------

                create_product_from_record(
                    record
                )

                # ------------------------------------------------
                # Product successfully created
                # ------------------------------------------------

                processed_rows += 1

            except Exception as row_error:

                failed_rows += 1

                ImportRowError.objects.create(
                    import_job=import_job,
                    row_number=index,
                    error_message=str(row_error),
                    raw_data=record,
                )

        # ----------------------------------------------------
        # Update counters
        # ----------------------------------------------------

        import_job.processed_rows = processed_rows
        import_job.failed_rows = failed_rows

        # ----------------------------------------------------
        # Final status
        # ----------------------------------------------------

        if failed_rows == 0:

            import_job.status = "COMPLETED"

        else:

            # Import itself completed, but some rows failed.
            import_job.status = "COMPLETED"

        import_job.completed_at = timezone.now()

        import_job.save(
            update_fields=[
                "processed_rows",
                "failed_rows",
                "status",
                "completed_at",
            ]
        )

        return import_job

    except Exception:

        # ----------------------------------------------------
        # Mark import as failed
        # ----------------------------------------------------

        import_job.status = "FAILED"

        import_job.completed_at = timezone.now()

        import_job.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

        # ----------------------------------------------------
        # Re-raise original error
        # ----------------------------------------------------

        raise