# CV Scanner

Ứng dụng phân tích CV, trích xuất thông tin và đối chiếu CV với Job Description.

## Yêu cầu

- Python 3.11
- Git

## Khởi tạo môi trường

```bash
python -m venv .venv
```

Kích hoạt môi trường trên Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Cài đặt thư viện phục vụ phát triển:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Tạo file biến môi trường cá nhân:

```powershell
Copy-Item .env.example .env
```

## Chạy ứng dụng

```bash
streamlit run app.py
```

## Kiểm tra trước khi tạo Pull Request

```bash
ruff check .
black --check .
```

## Quy trình làm việc

1. Cập nhật nhánh chính trước khi bắt đầu.
2. Tạo nhánh mới cho từng tính năng hoặc lỗi.
3. Không commit file `.env`, dữ liệu cá nhân, CV thật hoặc báo cáo được sinh ra.
4. Chạy lint và format check trước khi mở Pull Request.
5. Tạo Pull Request để thành viên khác review trước khi merge.

