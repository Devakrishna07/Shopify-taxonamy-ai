import pandas as pd

from django.utils import timezone

from .models import ImportRowError


# ============================================================
# COLUMN MAPPING
# ============================================================

COLUMN_MAPPING = {
    # Product ID
    "id": "external_product_id",
    "product_id": "external_product_id",
    "external_product_id": "external_product_id",

    # SKU
    "sku": "sku",

    # Title
    "title": "title",
    "product_title": "title",
    "name": "title",

    # Description
    "description": "description",

    # Brand
    "brand": "brand",

    # Product Type
    "product_type": "product_type",

    # Category
    "category": "existing_category",
    "existing_category": "existing_category",

    # Subcategory
    "subcategory": "existing_subcategory",
    "existing_subcategory": "existing_subcategory",

    # Images
    "image": "image_url",
    "image_url": "image_url",
    "image_urls": "image_url",
}


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "title",
]


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def normalize_column_name(column):
    """
    Convert an Excel/CSV column name into a standard format.

    Examples:
        "Product Title" -> "product_title"
        "Product-Type"  -> "product_type"
        " SKU "         -> "sku"
    """

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def normalize_columns(df):
    """
    Normalize dataframe column names and map supported
    external column names to our internal field names.
    """

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    rename_map = {}

    for column in df.columns:

        if column in COLUMN_MAPPING:
            rename_map[column] = COLUMN_MAPPING[column]

    df = df.rename(columns=rename_map)

    return df


# ============================================================
# COLUMN VALIDATION
# ============================================================

def validate_columns(df):
    """
    Validate that all required columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


# ============================================================
# VALUE CLEANING
# ============================================================

def clean_value(value):
    """
    Normalize individual cell values.

    Empty strings, NaN and None are converted to None.
    """

    if value is None:
        return None

    try:

        if pd.isna(value):
            return None

    except (TypeError, ValueError):
        pass

    value = str(value).strip()

    if value == "":
        return None

    return value


# ============================================================
# ROW NORMALIZATION
# ============================================================

def normalize_row(row):
    """
    Convert a pandas row into our internal product structure.
    """

    return {
        "external_product_id": clean_value(
            row.get("external_product_id")
        ),

        "sku": clean_value(
            row.get("sku")
        ),

        "title": clean_value(
            row.get("title")
        ),

        "description": clean_value(
            row.get("description")
        ),

        "brand": clean_value(
            row.get("brand")
        ),

        "product_type": clean_value(
            row.get("product_type")
        ),

        "existing_category": clean_value(
            row.get("existing_category")
        ),

        "existing_subcategory": clean_value(
            row.get("existing_subcategory")
        ),

        "image_url": clean_value(
            row.get("image_url")
        ),
    }


# ============================================================
# FILE READING
# ============================================================

def read_product_file(file):
    """
    Read an XLSX or CSV file into a pandas DataFrame.
    """

    filename = file.name.lower()

    if filename.endswith(".csv"):

        df = pd.read_csv(file)

    elif filename.endswith(".xlsx"):

        df = pd.read_excel(file)

    else:

        raise ValueError(
            "Only CSV and XLSX files are supported."
        )

    return df


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def product_exists(product_data):
    """
    Check whether the product already exists.

    Duplicate detection priority:

    1. external_product_id
    2. SKU
    3. title + brand

    The fallback title + brand check is only used when
    external_product_id and SKU are unavailable.
    """

    from products.models import Product

    external_product_id = product_data.get(
        "external_product_id"
    )

    sku = product_data.get("sku")

    title = product_data.get("title")

    brand = product_data.get("brand")

    # --------------------------------------------------------
    # Check external product ID
    # --------------------------------------------------------

    if external_product_id:

        return Product.objects.filter(
            external_product_id=external_product_id
        ).exists()

    # --------------------------------------------------------
    # Check SKU
    # --------------------------------------------------------

    if sku:

        return Product.objects.filter(
            sku=sku
        ).exists()

    # --------------------------------------------------------
    # Fallback: title + brand
    # --------------------------------------------------------

    if title:

        queryset = Product.objects.filter(
            title=title
        )

        if brand:

            queryset = queryset.filter(
                brand=brand
            )

        return queryset.exists()

    return False


# ============================================================
# IMAGE URL PARSING
# ============================================================

def extract_image_urls(image_value):
    """
    Convert an image field into a list of image URLs.

    Multiple URLs can be separated using:

        comma
        semicolon
        newline
    """

    if not image_value:
        return []

    value = str(image_value).strip()

    if not value:
        return []

    # Normalize separators
    value = value.replace(";", ",")
    value = value.replace("\n", ",")

    urls = []

    for url in value.split(","):

        url = url.strip()

        if url:
            urls.append(url)

    return urls


# ============================================================
# CREATE PRODUCT
# ============================================================

def create_product(product_data, import_job):
    """
    Create a Product using the completed Products module
    structure.

    Images are intentionally NOT stored directly on Product.
    They are stored through ProductImage.
    """

    from products.models import Product, ProductImage

    # --------------------------------------------------------
    # Validate title
    # --------------------------------------------------------

    if not product_data["title"]:

        raise ValueError(
            "Product title is required."
        )

    # --------------------------------------------------------
    # Check duplicate
    # --------------------------------------------------------

    if product_exists(product_data):

        raise ValueError(
            "Duplicate product detected."
        )

    # --------------------------------------------------------
    # Create Product
    # --------------------------------------------------------

    product = Product.objects.create(
        import_job=import_job,

        external_product_id=product_data[
            "external_product_id"
        ],

        sku=product_data["sku"],

        title=product_data["title"],

        description=product_data["description"],

        brand=product_data["brand"],

        product_type=product_data["product_type"],

        existing_category=product_data[
            "existing_category"
        ],

        existing_subcategory=product_data[
            "existing_subcategory"
        ],
    )

    # --------------------------------------------------------
    # Create ProductImage records
    # --------------------------------------------------------

    image_urls = extract_image_urls(
        product_data["image_url"]
    )

    for index, image_url in enumerate(image_urls):

        ProductImage.objects.create(
            product=product,
            image_url=image_url,
            sort_order=index,
        )

    return product


# ============================================================
# ROW ERROR RECORDING
# ============================================================

def record_row_error(
    import_job,
    row_number,
    error,
    row
):
    """
    Store a row-level import failure.
    """

    ImportRowError.objects.create(
        import_job=import_job,

        row_number=row_number,

        error_message=str(error),

        raw_data={
            key: str(value)
            for key, value in row.items()
        },
    )


# ============================================================
# MAIN IMPORT PROCESS
# ============================================================

def process_import(import_job, file):
    """
    Main product import process.

    Workflow:

        1. Set import status to RUNNING
        2. Read XLSX/CSV
        3. Normalize columns
        4. Validate columns
        5. Process every row independently
        6. Create Product
        7. Create ProductImage records
        8. Record row-level failures
        9. Update progress
        10. Mark import COMPLETED
    """

    # --------------------------------------------------------
    # Set import status
    # --------------------------------------------------------

    import_job.status = "RUNNING"

    import_job.save(
        update_fields=["status"]
    )

    try:

        # ====================================================
        # READ FILE
        # ====================================================

        df = read_product_file(file)

        # ====================================================
        # NORMALIZE COLUMNS
        # ====================================================

        df = normalize_columns(df)

        # ====================================================
        # VALIDATE COLUMNS
        # ====================================================

        validate_columns(df)

        # ====================================================
        # STORE TOTAL ROW COUNT
        # ====================================================

        import_job.total_rows = len(df)

        import_job.save(
            update_fields=["total_rows"]
        )

        # ====================================================
        # PROCESS EACH ROW
        # ====================================================

        for index, row in df.iterrows():

            # Excel/CSV header is row 1,
            # therefore first data row is row 2.
            row_number = index + 2

            try:

                # --------------------------------------------
                # Normalize row
                # --------------------------------------------

                product_data = normalize_row(row)

                # --------------------------------------------
                # Create product and images
                # --------------------------------------------

                create_product(
                    product_data=product_data,
                    import_job=import_job,
                )

                # --------------------------------------------
                # Successful row
                # --------------------------------------------

                import_job.processed_rows += 1

            except Exception as error:

                # --------------------------------------------
                # Failed row
                # --------------------------------------------

                import_job.failed_rows += 1

                record_row_error(
                    import_job=import_job,
                    row_number=row_number,
                    error=error,
                    row=row,
                )

            # ----------------------------------------------
            # Persist progress after every row
            # ----------------------------------------------

            import_job.save(
                update_fields=[
                    "processed_rows",
                    "failed_rows",
                ]
            )

        # ====================================================
        # IMPORT COMPLETED
        # ====================================================

        import_job.status = "COMPLETED"

        import_job.completed_at = timezone.now()

        import_job.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

    except Exception as error:

        # ====================================================
        # IMPORT-LEVEL FAILURE
        # ====================================================

        import_job.status = "FAILED"

        import_job.save(
            update_fields=["status"]
        )

        raise error