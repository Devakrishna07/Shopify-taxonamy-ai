import datetime
from .constants import COLUMN_ALIASES


class ColumnNormalizer:
    """
    Handles normalization of spreadsheet column headers and cell values.
    """

    @staticmethod
    def normalize_column_name(column) -> str:
        if column is None:
            return ""
        return str(column).strip().lower()

    @classmethod
    def map_alias_headers(cls, headers: list) -> list:
        mapped = []
        for header in headers:
            normalized = cls.normalize_column_name(header)
            mapped.append(COLUMN_ALIASES.get(normalized, normalized))
        return mapped

    @staticmethod
    def clean_value(value):
        if value is None:
            return None
        if isinstance(value, (datetime.datetime, datetime.date)):
            return value.isoformat()
        return value

    @staticmethod
    def string_value(value):
        if value is None:
            return None
        value_str = str(value).strip()
        return value_str if value_str != "" else None
