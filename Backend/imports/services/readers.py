import io
import csv
from abc import ABC, abstractmethod
import openpyxl
from .normalizer import ColumnNormalizer


class BaseStreamingReader(ABC):
    """
    Abstract Base Class for memory-efficient streaming file readers.
    Streams rows in chunks without loading entire files into memory.
    """

    @abstractmethod
    def stream_batches(self, file_obj, batch_size=500):
        """Yield (batch_records, batch_start_row_number, total_estimated)"""
        pass


class ExcelStreamingReader(BaseStreamingReader):
    """
    Memory-efficient Excel reader using openpyxl in read_only mode.
    Does not buffer full DOM into memory; memory usage is O(batch_size).
    """

    def stream_batches(self, file_obj, batch_size=500):
        # Open in read_only and data_only mode for lowest memory footprint
        wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
        sheet = wb.active

        rows_iter = sheet.iter_rows(values_only=True)

        # 1. Read and normalize header row
        try:
            header_row = next(rows_iter)
        except StopIteration:
            wb.close()
            return

        headers = [
            ColumnNormalizer.normalize_column_name(cell) if cell is not None else ""
            for cell in header_row
        ]
        headers = ColumnNormalizer.map_alias_headers(headers)

        batch = []
        current_row_num = 2  # 1 is header

        for row in rows_iter:
            if not any(row):  # skip completely empty row
                current_row_num += 1
                continue

            record = {}
            for col_idx, value in enumerate(row):
                if col_idx < len(headers):
                    col_name = headers[col_idx]
                    if col_name:
                        record[col_name] = ColumnNormalizer.clean_value(value)

            batch.append((current_row_num, record))
            current_row_num += 1

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch

        wb.close()


class CsvStreamingReader(BaseStreamingReader):
    """
    Memory-efficient CSV reader using native python csv.reader.
    Memory usage is O(batch_size).
    """

    def stream_batches(self, file_obj, batch_size=500):
        # Ensure text mode stream
        if hasattr(file_obj, "read"):
            content = file_obj.read()
            if isinstance(content, bytes):
                text_stream = io.StringIO(content.decode("utf-8", errors="replace"))
            else:
                text_stream = io.StringIO(content)
        else:
            text_stream = file_obj

        reader = csv.reader(text_stream)

        try:
            header_row = next(reader)
        except StopIteration:
            return

        headers = [
            ColumnNormalizer.normalize_column_name(cell) if cell is not None else ""
            for cell in header_row
        ]
        headers = ColumnNormalizer.map_alias_headers(headers)

        batch = []
        current_row_num = 2

        for row in reader:
            if not any(row):
                current_row_num += 1
                continue

            record = {}
            for col_idx, value in enumerate(row):
                if col_idx < len(headers):
                    col_name = headers[col_idx]
                    if col_name:
                        record[col_name] = ColumnNormalizer.clean_value(value)

            batch.append((current_row_num, record))
            current_row_num += 1

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch


class StreamingReaderFactory:
    """
    Factory resolving streaming reader strategy by filename extension.
    """

    _readers = {
        ".xlsx": ExcelStreamingReader,
        ".csv": CsvStreamingReader,
    }

    @classmethod
    def get_reader(cls, filename: str) -> BaseStreamingReader:
        filename_lower = filename.lower().strip()
        for ext, reader_cls in cls._readers.items():
            if filename_lower.endswith(ext):
                return reader_cls()

        raise ValueError(
            f"Unsupported file format for '{filename}'. Only CSV and XLSX are supported."
        )
