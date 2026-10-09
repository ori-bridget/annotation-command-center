# Annotation Command Center

Prototype MVP cho project build-phase: dashboard tiến độ/chất lượng, report studio và Annotation Assistant chỉ trả lời dựa trên guideline.

## Cấu trúc mã nguồn

- `app.py`: entrypoint và điều phối route.
- `annotation_app/data.py`: dữ liệu mẫu CVAT/GitHub/guideline và bộ lọc.
- `annotation_app/auth.py`: đăng nhập demo và phân quyền.
- `annotation_app/services.py`: sinh report, Q&A và xuất DOCX.
- `annotation_app/styles.py`: theme, top navigation và sidebar.
- `annotation_app/sidebar.py`: bộ lọc workspace và navigation.
- `annotation_app/pages.py`: UI cho Dashboard, Report Studio và Annotation Assistant.

## Tài khoản demo

| Username | Password | Role |
|---|---|---|
| `mentor` | `mentor123` | Mentor |
| `lead` | `lead123` | Lead |
| `member` | `member123` | Member |

Member có thể tạo/sửa/xuất report nhưng không được approve report. Chỉ Mentor mới được đóng câu hỏi trong mentor queue; Lead và Mentor được approve report. Đây là auth cho prototype local, chưa phải cơ chế bảo mật production.

## Chạy local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Prototype hiện dùng dữ liệu mẫu trong `app.py`. Các connector CVAT/GitHub sẽ được thay thế ở bước tiếp theo sau khi chốt API và mapping dữ liệu thật.
