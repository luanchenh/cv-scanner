"""Read text from PDF documents."""

from contextlib import contextmanager
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import BinaryIO, Iterator, TypeAlias

from pypdf import PdfReader
from pypdf.errors import DependencyError, PyPdfError

FileSource: TypeAlias = str | PathLike[str] | bytes | bytearray | BinaryIO


class PDFReaderError(Exception):
    pass


class PDFPasswordError(PDFReaderError):
    pass


@contextmanager
def _open_pdf(source: FileSource) -> Iterator[BinaryIO]:
    if isinstance(source, (str, PathLike)):
        path = Path(source)
        if path.suffix.lower() != ".pdf":
            raise PDFReaderError(f"Expected a .pdf file, received: {path.name}")
        if not path.is_file():
            raise PDFReaderError(f"PDF file does not exist: {path}")

        try:
            stream = path.open("rb")
        except OSError as exc:
            raise PDFReaderError(f"Unable to open PDF file: {path}") from exc
        try:
            yield stream
        finally:
            stream.close()
        return

    if isinstance(source, (bytes, bytearray)):
        if not source:
            raise PDFReaderError("PDF file is empty.")
        with BytesIO(source) as stream:
            yield stream
        return

    if not hasattr(source, "read"):
        raise TypeError("PDF source must be a path, bytes, or a binary file-like object.")

    original_position: int | None = None
    try:
        original_position = source.tell()
    except (AttributeError, OSError):
        pass

    try:
        source.seek(0)
    except (AttributeError, OSError) as exc:
        raise PDFReaderError("PDF stream must support binary read and seek operations.") from exc

    try:
        yield source
    finally:
        if original_position is not None:
            try:
                source.seek(original_position)
            except OSError:
                pass


def _create_reader(stream: BinaryIO, password: str | bytes | None) -> PdfReader:
    try:
        reader = PdfReader(stream, strict=False)
    except (PyPdfError, OSError, ValueError) as exc:
        raise PDFReaderError("The file is empty, damaged, or not a valid PDF.") from exc

    if not reader.is_encrypted:
        return reader

    try:
        decryption_result = reader.decrypt(password or "")
    except (DependencyError, PyPdfError, ValueError) as exc:
        raise PDFPasswordError("Unable to decrypt the PDF with the supplied password.") from exc

    if int(decryption_result) == 0:
        message = "This PDF is password-protected."
        if password is not None:
            message = "The supplied PDF password is incorrect."
        raise PDFPasswordError(message)

    return reader


def read_pdf_pages(source: FileSource, password: str | bytes | None = None) -> list[str]:
    with _open_pdf(source) as stream:
        reader = _create_reader(stream, password)
        pages: list[str] = []

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except (PyPdfError, OSError, ValueError) as exc:
                raise PDFReaderError(
                    f"Unable to extract text from PDF page {page_number}."
                ) from exc
            pages.append(text.strip())

        return pages


def read_pdf(source: FileSource, password: str | bytes | None = None) -> str:
    return "\n\n".join(read_pdf_pages(source, password=password)).strip()


__all__ = [
    "FileSource",
    "PDFPasswordError",
    "PDFReaderError",
    "read_pdf",
    "read_pdf_pages",
]
