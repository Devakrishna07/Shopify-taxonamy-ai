from .constants import REQUIRED_COLUMNS


class ImportValidator:
    """
    Validates schema and individual row requirements.
    """

    @staticmethod
    def validate_required_headers(headers: list):
        missing = [col for col in REQUIRED_COLUMNS if col not in headers]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    @staticmethod
    def validate_row_record(record: dict):
        title = record.get("title")
        if title is None or str(title).strip() == "":
            raise ValueError("Product title is empty.")
