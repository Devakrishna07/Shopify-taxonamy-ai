"""
Imports service package exposing public interfaces.
"""

from .processor import ImportProcessor
from .readers import (
    StreamingReaderFactory,
    BaseStreamingReader,
    ExcelStreamingReader,
    CsvStreamingReader,
)
from .normalizer import ColumnNormalizer
from .validator import ImportValidator
from .product_creator import ProductRecordCreator


def process_import(import_job, uploaded_file):
    """
    Backwards-compatible procedural entry point.
    """
    processor = ImportProcessor()
    return processor.process(import_job, uploaded_file)


__all__ = [
    "ImportProcessor",
    "process_import",
    "StreamingReaderFactory",
    "BaseStreamingReader",
    "ExcelStreamingReader",
    "CsvStreamingReader",
    "ColumnNormalizer",
    "ImportValidator",
    "ProductRecordCreator",
]
