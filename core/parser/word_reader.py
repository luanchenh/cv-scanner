
"""Read text from Microsoft Word DOCX documents."""

from contextlib import contextmanager
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import BinaryIO, Iterator, TypeAlias
from zipfile import BadZipFile

from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.table import Table
from docx.text.paragraph import Paragraph

FileSource: TypeAlias = str | PathLike[str] | bytes | bytearray | BinaryIO


class DOCXReaderError(Exception):
    """Raised when a DOCX document cannot be opened or parsed."""


@contextmanager
def _open_docx(source: FileSource) -> Iterator[BinaryIO]:
    if isinstance(source, (str, PathLike)):
        path = Path(source)
        if path.suffix.lower() != ".docx":
            raise DOCXReaderError(f"Expected a .docx file, received: {path.name}")
        if not path.is_file():
            raise DOCXReaderError(f"DOCX file does not exist: {path}")

        try:
            stream = path.open("rb")
        except OSError as exc:
            raise DOCXReaderError(f"Unable to open DOCX file: {path}") from exc
        try:
            yield stream
        finally:
            stream.close()
        return

    if isinstance(source, (bytes, bytearray)):
        if not source:
            raise DOCXReaderError("DOCX file is empty.")
        with BytesIO(source) as stream:
            yield stream
        return

    if not hasattr(source, "read"):
        raise TypeError("DOCX source must be a path, bytes, or a binary file-like object.")

    original_position: int | None = None
    try:
        original_position = source.tell()
    except (AttributeError, OSError):
        pass

    try:
        source.seek(0)
    except (AttributeError, OSError) as exc:
        raise DOCXReaderError("DOCX stream must support binary read and seek operations.") from exc

    try:
        yield source
    finally:
        if original_position is not None:
            try:
                source.seek(original_position)
            except OSError:
                pass


def _table_to_text(table: Table) -> str:
    rows: list[str] = []
    for row in table.rows:
        cells = [" ".join(cell.text.split()) for cell in row.cells]
        if any(cells):
            rows.append("\t".join(cells).rstrip())
    return "\n".join(rows)


def read_docx(source: FileSource) -> str:

    with _open_docx(source) as stream:
        try:
            document = Document(stream)
            blocks: list[str] = []

            for item in document.iter_inner_content():
                if isinstance(item, Paragraph):
                    text = item.text.strip()
                elif isinstance(item, Table):
                    text = _table_to_text(item)
                else:
                    continue

                if text:
                    blocks.append(text)

            return "\n\n".join(blocks).strip()
        except (BadZipFile, KeyError, OSError, PackageNotFoundError, ValueError) as exc:
            raise DOCXReaderError("The file is damaged or not a valid DOCX document.") from exc


__all__ = ["DOCXReaderError", "FileSource", "read_docx"]
