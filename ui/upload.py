"""Reusable Streamlit file-upload components."""

from pathlib import Path

import streamlit as st
from streamlit.typing import UploadedFile

ALLOWED_CV_EXTENSIONS = ("pdf", "docx")
DEFAULT_MAX_UPLOAD_SIZE_MB = 10


def _format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024**2:.1f} MB"


def render_cv_uploader(
    *,
    key: str = "cv_uploader",
    max_size_mb: int = DEFAULT_MAX_UPLOAD_SIZE_MB,
) -> UploadedFile | None:

    if max_size_mb <= 0:
        raise ValueError("max_size_mb must be greater than zero.")

    uploaded_file = st.file_uploader(
        "Tải CV lên",
        type=list(ALLOWED_CV_EXTENSIONS),
        accept_multiple_files=False,
        key=key,
        help=f"Hỗ trợ PDF hoặc DOCX, tối đa {max_size_mb} MB.",
        max_upload_size=max_size_mb,
    )

    if uploaded_file is None:
        return None

    extension = Path(uploaded_file.name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_CV_EXTENSIONS:
        st.error("Định dạng không hợp lệ. Vui lòng chọn file PDF hoặc DOCX.")
        return None

    if uploaded_file.size == 0:
        st.error("File đã tải lên đang rỗng.")
        return None

    max_size_bytes = max_size_mb * 1024**2
    if uploaded_file.size > max_size_bytes:
        st.error(f"File vượt quá giới hạn {max_size_mb} MB.")
        return None

    st.caption(
        f"Đã chọn: {uploaded_file.name} · {_format_file_size(uploaded_file.size)}"
    )
    return uploaded_file


__all__ = [
    "ALLOWED_CV_EXTENSIONS",
    "DEFAULT_MAX_UPLOAD_SIZE_MB",
    "render_cv_uploader",
]
