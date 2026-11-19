"""
Column aliases and default mappings for importing product catalogs.
"""

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

REQUIRED_COLUMNS = [
    "title",
]
