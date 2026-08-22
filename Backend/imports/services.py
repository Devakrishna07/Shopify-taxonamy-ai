import csv
import io
from datetime import datetime

import pandas as pd

from .models import ImportJob, ImportRowError


# ============================================================
# COLUMN ALIASES
# ============================================================
#
# The frontend/import module uses a standard internal field
# called "title".
#
# Your actual Excel file uses:
#
#     Product Name
#
# Therefore we normalize Product Name -> title.
#
# Additional aliases are included so future CSV/XLSX files
# can use common variations.
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

        "Product Name"       -> "product name"
        "Product Description " -> "product description"
    """

    if column is None:
        return ""

    return str(column).strip().lower()


def normalize_dataframe_columns(dataframe):
    """
    Convert external spreadsheet column names into the
    internal names used by the import pipeline.
    """

    rename_map = {}

    for column in dataframe.columns:
        normalized = normalize_column_name(column)

        if normalized in COLUMN_ALIASES:
            rename_map[column] = COLUMN_ALIASES[normalized]

    dataframe = dataframe.rename(columns=rename_map)

    return dataframe


def clean_value(value):
    """
    Convert pandas values into JSON/database-friendly values.
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

    The internal import pipeline requires a product title.

    The actual uploaded file can provide this as:

        Product Name

    because it has already been normalized to:

        title
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
# PROCESS IMPORT
# ============================================================

def process_import(import_job, uploaded_file):
    """
    Main import processor.

    Responsibilities:

    1. Read CSV/XLSX
    2. Normalize column names
    3. Validate required fields
    4. Count rows
    5. Track row-level errors
    6. Update ImportJob status
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
            """
            Excel row numbers start at 2 because
            row 1 contains the header.
            """

            try:

                title = record.get("title")

                # --------------------------------------------
                # Validate title
                # --------------------------------------------

                if (
                    title is None
                    or str(title).strip() == ""
                ):
                    raise ValueError(
                        "Product title is empty."
                    )

                # --------------------------------------------
                # At this point the row is valid.
                #
                # The normalized record is ready for the
                # downstream processing module.
                # --------------------------------------------

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
            import_job.status = "COMPLETED"

        import_job.completed_at = datetime.now()

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

        import_job.completed_at = datetime.now()

        import_job.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

        # ----------------------------------------------------
        # Re-raise the original error so views.py can return
        # it to the frontend.
        # ----------------------------------------------------

        raise