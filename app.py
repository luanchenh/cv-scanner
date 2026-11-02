"""Streamlit entry point for CV Scanner."""

from pathlib import Path

import streamlit as st

from core.parser import (
    DOCXReaderError,
    PDFPasswordError,
    PDFReaderError,
    read_docx,
    read_pdf,
)
from ui import render_cv_uploader

st.set_page_config(
    page_title="CV Scanner",
    page_icon="📄",
    layout="centered",
)


@st.cache_data(show_spinner=False)
def _extract_text(file_name: str, file_content: bytes, password: str | None) -> str:
    extension = Path(file_name).suffix.lower()
    if extension == ".pdf":
        return read_pdf(file_content, password=password or None)
    if extension == ".docx":
        return read_docx(file_content)
    raise ValueError("Unsupported file extension.")


def main() -> None:
    st.title("CV Scanner")
    st.write("Tải CV định dạng PDF hoặc DOCX để trích xuất nội dung.")

    uploaded_file = render_cv_uploader()
    if uploaded_file is None:
        return

    extension = Path(uploaded_file.name).suffix.lower()
    password: str | None = None
    if extension == ".pdf":
        password = st.text_input(
            "Mật khẩu PDF (nếu có)",
            type="password",
            help="Để trống nếu PDF không được bảo vệ bằng mật khẩu.",
        )

    try:
        with st.spinner("Đang đọc nội dung CV..."):
            extracted_text = _extract_text(
                uploaded_file.name,
                uploaded_file.getvalue(),
                password,
            )
    except PDFPasswordError as exc:
        st.warning(str(exc))
        return
    except (DOCXReaderError, PDFReaderError, ValueError) as exc:
        st.error(f"Không thể đọc CV: {exc}")
        return

    if not extracted_text:
        st.warning(
            "Không tìm thấy văn bản trong file. PDF có thể là bản scan và cần OCR."
        )
        return

    st.success("Đã đọc CV thành công.")
    with st.expander("Xem nội dung đã trích xuất", expanded=True):
        st.text_area(
            "Nội dung CV",
            value=extracted_text,
            height=400,
            disabled=True,
            label_visibility="collapsed",
        )


if __name__ == "__main__":
    main()
