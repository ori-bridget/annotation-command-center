# Annotation Command Center

Prototype MVP cho project build-phase: dashboard tiến độ/chất lượng, report studio và Annotation Assistant chỉ trả lời dựa trên guideline.

## Chạy local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Prototype hiện dùng dữ liệu mẫu trong `app.py`. Các connector CVAT/GitHub sẽ được thay thế ở bước tiếp theo sau khi chốt API và mapping dữ liệu thật.
