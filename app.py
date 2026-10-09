from __future__ import annotations

import io
import html
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import altair as alt
from docx import Document
from docx.shared import Pt


st.set_page_config(
    page_title="Annotation Command Center",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="auto",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #17212b;
        --muted: #70808f;
        --line: #e5e9ee;
        --paper: #fbfcfe;
        --navy: #132b43;
        --blue: #2d6cdf;
        --mint: #36a995;
        --amber: #d89024;
        --red: #d85b61;
    }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em; }
    .block-container { padding-top: 2.2rem; max-width: 1440px; }
    [data-testid="stSidebar"] { background: #101a2b; border-right: 1px solid #26364a; color: #edf4fb; }
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] { color: #edf4fb !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    span[data-testid="stTooltipIcon"]:has(button p) { position: fixed !important; left: 8px !important; top: 12px !important; z-index: 999999 !important; }
    span[data-testid="stTooltipIcon"]:has(button p) button { min-width: 44px !important; width: 44px !important; height: 44px !important; padding: 0 !important; border-radius: 8px !important; background: #1e293b !important; border: 1px solid #52657d !important; color: #f8fafc !important; }
    [data-testid="stMetric"] { background: white; border: 1px solid var(--line); padding: 16px 18px; border-radius: 14px; }
    [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; font-size: 1.65rem; }
    .hero { background: linear-gradient(120deg, #102940 0%, #1e4565 70%, #286e78 100%); color: white; border-radius: 20px; padding: 28px 32px; margin-bottom: 24px; }
    .hero h1 { color: white; margin: 0 0 8px 0; font-size: 2.2rem; }
    .hero p { color: #cfe0ed; margin: 0; max-width: 700px; font-size: 1rem; }
    .eyebrow { text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 700; color: #89c9c0; margin-bottom: 8px; }
    .section-title { margin-top: 10px; margin-bottom: 12px; }
    .small-muted { color: var(--muted); font-size: .86rem; }
    .status-pill { display: inline-block; border-radius: 20px; padding: 4px 10px; font-size: .76rem; font-weight: 700; }
    .status-good { background: #e4f5ef; color: #187d68; }
    .status-warn { background: #fff2d9; color: #9d6811; }
    .status-danger { background: #fde8e8; color: #aa4047; }
    .source-card { border: 1px solid var(--line); border-radius: 12px; padding: 13px 15px; background: white; margin: 6px 0; }
    .source-card strong { color: var(--navy); }
    .report-card { background: white; border: 1px solid var(--line); border-radius: 16px; padding: 22px 24px; }
    .readonly-example { height: 620px; overflow: auto; background: #20232d; color: #f1f3f5; border: 1px solid #3a4050; border-radius: 8px; padding: 14px 16px; font-family: 'Cascadia Mono', 'Consolas', monospace; font-size: .82rem; line-height: 1.45; white-space: pre-wrap; }
    .readonly-example pre { margin: 0; font: inherit; white-space: pre-wrap; }
    .report-card h3 { margin-top: 0; color: var(--navy); }
    .callout { border-left: 4px solid var(--mint); background: #edf8f6; padding: 14px 16px; border-radius: 0 10px 10px 0; }
    div[data-testid="stTabs"] button { font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


JOBS = [
    {"job_id": "JOB-2048", "batch": "Batch Alpha", "category": "2D Bounding Box", "assignee": "Linh", "status": "Completed", "score": 96, "edits": 1, "age": 2, "hard": False},
    {"job_id": "JOB-2049", "batch": "Batch Alpha", "category": "2D Bounding Box", "assignee": "Minh", "status": "In review", "score": 84, "edits": 3, "age": 4, "hard": True},
    {"job_id": "JOB-2050", "batch": "Batch Alpha", "category": "2D Bounding Box", "assignee": "An", "status": "Completed", "score": 91, "edits": 1, "age": 1, "hard": False},
    {"job_id": "JOB-2051", "batch": "Batch Alpha", "category": "Tracking", "assignee": "Linh", "status": "In progress", "score": 78, "edits": 5, "age": 6, "hard": True},
    {"job_id": "JOB-2052", "batch": "Batch Alpha", "category": "Tracking", "assignee": "Minh", "status": "Blocked", "score": 72, "edits": 4, "age": 8, "hard": True},
    {"job_id": "JOB-2053", "batch": "Batch Alpha", "category": "Tracking", "assignee": "An", "status": "Completed", "score": 94, "edits": 0, "age": 2, "hard": False},
    {"job_id": "JOB-2054", "batch": "Batch Alpha", "category": "3D LiDAR", "assignee": "Linh", "status": "In progress", "score": 88, "edits": 2, "age": 3, "hard": False},
    {"job_id": "JOB-2055", "batch": "Batch Alpha", "category": "3D LiDAR", "assignee": "Minh", "status": "In review", "score": 76, "edits": 4, "age": 5, "hard": True},
]

ISSUES = [
    {"id": "#184", "title": "Occluded object: when should it be labeled?", "label": "annotation-question", "status": "Open", "job_id": "JOB-2051", "category": "Tracking"},
    {"id": "#181", "title": "Track ID changes after full occlusion", "label": "annotation-question", "status": "Open", "job_id": "JOB-2052", "category": "Tracking"},
    {"id": "#176", "title": "Small object threshold clarification", "label": "guideline", "status": "Resolved", "job_id": "JOB-2049", "category": "2D Bounding Box"},
    {"id": "#171", "title": "Add validation sample for truncation", "label": "process", "status": "Resolved", "job_id": "JOB-2048", "category": "2D Bounding Box"},
    {"id": "#188", "title": "Sparse point cloud: minimum evidence for a cuboid", "label": "annotation-question", "status": "Open", "job_id": "JOB-2055", "category": "3D LiDAR"},
]

GUIDELINES = [
    {"doc": "2D Bounding Box Guideline", "version": "v2.1", "week": "Week 41", "category": "2D Bounding Box", "section": "Occlusion", "page": "p. 8", "text": "When an object is partially occluded but enough visual evidence remains to identify its visible extent, annotate the visible bounding box and mark the occlusion attribute as true."},
    {"doc": "2D Bounding Box Guideline", "version": "v2.1", "week": "Week 41", "category": "2D Bounding Box", "section": "Small objects", "page": "p. 11", "text": "Objects smaller than 6 by 6 pixels should not be annotated unless they are part of an already established tracking sequence."},
    {"doc": "Tracking Guideline", "version": "v1.4", "week": "Week 41", "category": "Tracking", "section": "Full occlusion", "page": "p. 14", "text": "Keep the same track ID through a full occlusion when the object can be confidently matched after it reappears. Start a new track only when the identity cannot be determined."},
    {"doc": "Tracking Guideline", "version": "v1.4", "week": "Week 40", "category": "Tracking", "section": "Track creation", "page": "p. 5", "text": "Create a new track when an object first enters the visible scene. Do not reuse a previous ID when identity is uncertain."},
    {"doc": "3D LiDAR Guideline", "version": "v1.0", "week": "Week 41", "category": "3D LiDAR", "section": "Sparse point cloud", "page": "p. 6", "text": "Annotate a 3D cuboid only when the point cloud provides enough evidence to determine the object's center, dimensions, and orientation. Do not infer a cuboid from a few isolated points."},
    {"doc": "3D LiDAR Guideline", "version": "v1.0", "week": "Week 41", "category": "3D LiDAR", "section": "Occlusion", "page": "p. 9", "text": "For a partially occluded object, fit the cuboid to the visible point cloud and use contextual evidence only when the guideline-defined object extent is still identifiable."},
]


def init_state() -> None:
    if "guidelines" not in st.session_state:
        st.session_state.guidelines = list(GUIDELINES)
    if "report_text" not in st.session_state:
        st.session_state.report_text = ""
    if "report_status" not in st.session_state:
        st.session_state.report_status = "Draft"
    if "mentor_queue" not in st.session_state:
        st.session_state.mentor_queue = []
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    if "sidebar_open" not in st.session_state:
        st.session_state.sidebar_open = True
    if st.session_state.get("report_ui_version") != 2:
        st.session_state.report_text = ""
        st.session_state.report_format = None
        st.session_state.report_ui_version = 2


def filtered_jobs(batch: str, category: str) -> list[dict[str, Any]]:
    return [j for j in JOBS if (batch == "All batches" or j["batch"] == batch) and (category == "All categories" or j["category"] == category)]


def filtered_guidelines(week: str, category: str, question: str) -> list[dict[str, Any]]:
    terms = set(re.findall(r"[\wÀ-ỹ]+", question.lower()))
    candidates = []
    for item in st.session_state.guidelines:
        if week != "All weeks" and item["week"] != week:
            continue
        if category != "All categories" and item["category"] != category:
            continue
        corpus = f"{item['section']} {item['text']}".lower()
        score = sum(1 for term in terms if len(term) > 2 and term in corpus)
        if score:
            candidates.append((score, item))
    return [item for _, item in sorted(candidates, key=lambda value: value[0], reverse=True)]


def build_answer(question: str, sources: list[dict[str, Any]]) -> tuple[str, str]:
    if not sources:
        return (
            "Mình chưa tìm thấy quy định phù hợp trong guideline đã chọn. "
            "Câu hỏi cần được mentor xác nhận; hệ thống không tự suy đoán.",
            "needs_review",
        )
    best = sources[0]
    return (
        f"Theo guideline, {best['text']}\n\n"
        f"Phạm vi áp dụng: {best['category']} · {best['week']} · {best['version']}",
        "answered",
    )


def make_report(jobs: list[dict[str, Any]], issues: list[dict[str, Any]]) -> str:
    total = len(jobs)
    completed = sum(j["status"] == "Completed" for j in jobs)
    avg_score = round(sum(j["score"] for j in jobs) / total, 1) if total else 0
    hard_jobs = [j for j in jobs if j["hard"]]
    open_issues = [i for i in issues if i["status"] == "Open"]
    hard_lines = "\n".join(f"- {j['job_id']}: điểm {j['score']}, {j['edits']} lần sửa — cần xem xét." for j in hard_jobs) or "- Chưa phát hiện ca khó."
    issue_lines = "\n".join(f"- {i['id']} — {i['title']} ({i['job_id']})" for i in open_issues) or "- Không có câu hỏi mở."
    return f"""# Báo cáo trước phiên mentor

**Batch:** {jobs[0]['batch'] if jobs else 'Chưa chọn'}  
**Tạo lúc:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 1. Tiến độ và kết quả

- Hoàn thành **{completed}/{total} job** ({round(completed / total * 100) if total else 0}%).
- Điểm trung bình: **{avg_score}/100**.
- Dữ liệu được tổng hợp từ CVAT và GitHub issues đã lọc.

## 2. Chất lượng và ca khó

{hard_lines}

## 3. Vấn đề và câu hỏi cần mentor

{issue_lines}

## 4. Kế hoạch tiếp theo

- Mentor xác nhận các câu hỏi đang mở.
- Rà soát các job có điểm thấp hoặc nhiều lần sửa.
- Cập nhật guideline/FAQ nếu có kết luận mới.
"""


def make_weekly_report(jobs: list[dict[str, Any]], issues: list[dict[str, Any]], week: str) -> str:
    """Generate the weekly journal format based on the user's tuan-01 example."""
    total = len(jobs)
    completed = sum(j["status"] == "Completed" for j in jobs)
    progress = round(completed / total * 100) if total else 0
    avg_score = round(sum(j["score"] for j in jobs) / total, 1) if total else 0
    open_issues = [i for i in issues if i["status"] == "Open"]
    rows = []
    for index, job in enumerate(jobs, start=1):
        icon = "✅" if job["status"] == "Completed" else "⛔" if job["status"] == "Blocked" else "🟡" if job["status"] in {"In progress", "In review"} else "⬜"
        rows.append(f"| {index} | {job['job_id']} — {job['category']} | @{job['assignee'].lower()} | — | {icon} {job['score']} điểm | {job['status']} · {job['edits']} lần sửa |")
    job_rows = "\n".join(rows) or "| — | Chưa có job trong bộ lọc | — | — | ⬜ 0% | — |"
    issue_lines = "\n".join(f"- {issue['id']} ({issue['job_id']}): {issue['title']}" for issue in open_issues) or "- Không có vướng mắc đang mở."
    next_week = "\n".join(f"- Xử lý {issue['id']} và cập nhật kết luận cho {issue['job_id']}." for issue in open_issues) or "- Tiếp tục hoàn thành và review các job còn lại."
    data_scope = jobs[0]["batch"] if jobs else "Chưa chọn batch"
    return f"""# Nhật ký tuần · {week}

**Lead tuần này:** Nhóm trưởng  
**Dữ liệu / task CVAT:** {data_scope}

## Thành viên và phân công

| Thành viên | Vị trí | Phân công tuần này |
|---|---|---|
| {', '.join(sorted({j['assignee'] for j in jobs})) or 'Chưa có dữ liệu'} | Annotator / Reviewer | Theo dõi các job trong batch đã chọn |

## Công việc

| # | Nội dung công việc | Annotator | Reviewer | Hoàn thành | Ghi chú |
|---|---|---|---|---|---|
{job_rows}

Mức hoàn thành hiện tại: **{progress}%** · Điểm trung bình: **{avg_score}/100**

## Tổng kết

- Đã hoàn thành: {completed} / {total} job ({progress}%).
- Job cần chú ý: {sum(j['hard'] for j in jobs)}.
- Câu hỏi GitHub đang mở: {len(open_issues)}.

## Vướng mắc

{issue_lines}

## Kế hoạch tuần tiếp theo

{next_week}
"""


def read_weekly_template(filename: str) -> str:
    template_path = Path(__file__).parent / "templates" / filename
    return template_path.read_text(encoding="utf-8") if template_path.exists() else ""


def safe_download_name(name: str, extension: str) -> str:
    cleaned = re.sub(r"[^\w\- ]+", "", name, flags=re.UNICODE).strip()
    cleaned = cleaned or "mentor-report"
    return f"{cleaned}{extension}"


def report_to_docx(markdown: str) -> bytes:
    """Create a lightweight DOCX export without requiring a markdown parser."""
    document = Document()
    styles = document.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10.5)
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            document.add_heading(stripped[2:], level=0)
        elif stripped.startswith("## "):
            document.add_heading(stripped[3:], level=1)
        elif stripped.startswith("- "):
            document.add_paragraph(stripped[2:], style="List Bullet")
        else:
            paragraph = document.add_paragraph()
            # Keep the export readable while preserving the common Markdown emphasis.
            parts = re.split(r"(\*\*.*?\*\*)", stripped)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = paragraph.add_run(part[2:-2])
                    run.bold = True
                else:
                    paragraph.add_run(part)
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def render_sidebar() -> tuple[str, str, str]:
    nav_left = "272px" if st.session_state.sidebar_open else "62px"
    st.markdown(
        f"""
        <style>
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) {{
            position: fixed !important;
            top: 0 !important;
            left: {nav_left} !important;
            right: 0 !important;
            z-index: 1000001 !important;
            padding: 12px 24px 10px !important;
            background: #0b111a !important;
            border-bottom: 1px solid #26364a !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, .18) !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioGroup"] {{
            gap: 0 !important;
            align-items: stretch !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] {{
            min-height: 38px !important;
            padding: 10px 16px !important;
            border-radius: 0 !important;
            color: #e7edf5 !important;
            cursor: pointer !important;
            transition: background .15s ease, color .15s ease !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] > div > div:first-child {{
            display: none !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] > div {{
            gap: 0 !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] p {{
            margin: 0 !important;
            color: inherit !important;
            font-size: .95rem !important;
            white-space: nowrap !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"]:hover {{
            background: #1d2b3c !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {{
            background: #f2a65a !important;
            color: #17212b !important;
            font-weight: 700 !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) {{
            background: #111d2d !important;
            border: 1px solid #33465e !important;
            border-radius: 14px !important;
            padding: 10px 12px !important;
            margin: 8px 0 18px !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioGroup"] {{
            gap: 0 !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] {{
            min-height: 38px !important;
            padding: 10px 22px !important;
            border-radius: 0 !important;
            color: #e7edf5 !important;
            cursor: pointer !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] > div > div:first-child {{
            display: none !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] > div {{
            gap: 0 !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] p {{
            margin: 0 !important;
            color: inherit !important;
            white-space: nowrap !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {{
            background: #f2a65a !important;
            color: #17212b !important;
            font-weight: 700 !important;
        }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"]:hover {{
            background: #1d2b3c !important;
        }}
        [data-testid="stAppViewContainer"] .main .block-container {{
            padding-top: 5.8rem !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    if not st.session_state.sidebar_open:
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] {
                display: block !important;
                width: 62px !important;
                min-width: 62px !important;
                max-width: 62px !important;
                overflow: hidden !important;
            }
            section[data-testid="stSidebar"] > div,
            section[data-testid="stSidebar"] * {
                width: 62px !important;
                min-width: 62px !important;
                max-width: 62px !important;
                overflow: hidden !important;
                visibility: hidden !important;
                opacity: 0 !important;
            }
            [data-testid="stSidebarCollapsedControl"] { display: none; }
            span[data-testid="stTooltipIcon"]:has(button p) {
                position: fixed !important;
                left: 8px !important;
                top: 12px !important;
                z-index: 999999 !important;
            }
            span[data-testid="stTooltipIcon"]:has(button p) button {
                min-width: 44px !important;
                width: 44px !important;
                height: 44px !important;
                padding: 0 !important;
                border-radius: 8px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    with st.sidebar:
        st.markdown("### ◆ Annotation OS")
        st.caption("MVP · Report + Guideline Assistant")
        st.caption("☰ Dùng nút ở đầu trang để thu/mở thanh tùy chọn")
        st.divider()
        st.markdown("**Workspace**")
        st.selectbox("Nguồn dữ liệu", ["Demo workspace", "CVAT + GitHub (sắp kết nối)"], label_visibility="collapsed")
        batches = ["All batches"] + sorted({j["batch"] for j in JOBS})
        categories = ["All categories"] + sorted({j["category"] for j in JOBS})
        weeks = ["All weeks"] + sorted({g["week"] for g in st.session_state.guidelines})
        batch = st.selectbox("Batch", batches)
        category = st.selectbox("Job category", categories)
        week = st.selectbox("Guideline week", weeks)
    return batch, category, week


def dashboard_page(jobs: list[dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    st.markdown('<div class="eyebrow">Mentor preparation workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Build clarity before the mentor session.</h1><p>The command center for progress, quality signals, open questions and guideline-backed answers.</p></div>', unsafe_allow_html=True)

    total = len(jobs)
    completed = sum(j["status"] == "Completed" for j in jobs)
    avg_score = round(sum(j["score"] for j in jobs) / total, 1) if total else 0
    open_issues = sum(i["status"] == "Open" for i in issues)
    hard = sum(j["hard"] for j in jobs)
    a, b, c, d = st.columns(4)
    a.metric("Completion", f"{round(completed / total * 100) if total else 0}%", f"{completed}/{total} jobs")
    b.metric("Average score", f"{avg_score}/100", "Across selected jobs")
    c.metric("Hard cases", hard, "Needs review" if hard else "All clear")
    d.metric("Open questions", open_issues, "From filtered issues")

    st.markdown("### Progress overview")
    left, right = st.columns([1.2, 1])
    with left:
        status_df = pd.DataFrame(jobs)
        if not status_df.empty:
            status_counts = status_df["status"].value_counts().rename_axis("Status").reset_index(name="Jobs")
            st.markdown("**Số lượng job theo trạng thái**")
            progress_chart = (
                alt.Chart(status_counts)
                .mark_bar(color="#36a995", cornerRadiusEnd=5)
                .encode(
                    x=alt.X("Jobs:Q", scale=alt.Scale(domainMin=0), axis=alt.Axis(title=None, format="d")),
                    y=alt.Y("Status:N", sort="-x", axis=alt.Axis(title=None, labelLimit=180)),
                    tooltip=[alt.Tooltip("Status:N", title="Trạng thái"), alt.Tooltip("Jobs:Q", title="Số lượng job", format="d")],
                )
                .properties(height=240)
            )
            st.altair_chart(progress_chart, width="stretch")
    with right:
        st.markdown("#### Data sources")
        st.markdown(f'<div class="source-card"><strong>CVAT</strong><br><span class="small-muted">{len(JOBS)} jobs · {len({j["batch"] for j in JOBS})} batch · synced successfully</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="source-card"><strong>GitHub</strong><br><span class="small-muted">{len(ISSUES)} issues · {sum(i["status"] == "Open" for i in ISSUES)} open annotation questions</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="source-card"><strong>Guidelines</strong><br><span class="small-muted">{len(st.session_state.guidelines)} chunks · {len({g["category"] for g in st.session_state.guidelines})} categories · {len({g["week"] for g in st.session_state.guidelines})} weeks</span></div>', unsafe_allow_html=True)

    st.markdown("### Quality signals")
    left, right = st.columns([1.15, 1])
    with left:
        hard_rows = [j for j in jobs if j["hard"]]
        if hard_rows:
            hard_df = pd.DataFrame(hard_rows)[["job_id", "category", "assignee", "score", "edits", "age"]]
            hard_df.columns = ["Job", "Category", "Assignee", "Score", "Edits", "Age (days)"]
            st.dataframe(hard_df, hide_index=True, width="stretch")
        else:
            st.success("No hard cases in the current filter.")
    with right:
        issue_rows = [i for i in issues if i["status"] == "Open"]
        for issue in issue_rows:
            st.markdown(f'<div class="source-card"><span class="status-pill status-warn">{issue["id"]}</span> <strong>{issue["title"]}</strong><br><span class="small-muted">{issue["job_id"]} · {issue["category"]}</span></div>', unsafe_allow_html=True)

    st.markdown("### Job detail")
    table = pd.DataFrame(jobs)
    if not table.empty:
        table = table[["job_id", "category", "assignee", "status", "score", "edits"]]
        table.columns = ["Job", "Category", "Assignee", "Status", "Score", "Edits"]
        st.dataframe(table, hide_index=True, width="stretch")


def report_page(jobs: list[dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    st.markdown('<div class="eyebrow">Report studio</div>', unsafe_allow_html=True)
    st.title("Mentor report")
    st.caption("Numbers are computed from the filtered dataset. AI is used only to turn structured facts into readable prose.")
    report_format = st.radio("Report format", ["Weekly journal", "Mentor report · 4 sections"], horizontal=True)
    if st.session_state.get("report_format") != report_format:
        st.session_state.report_format = report_format
        st.session_state.report_text = read_weekly_template("_mau-tuan.md") if report_format == "Weekly journal" else make_report(jobs, issues)
    if not st.session_state.report_text:
        st.session_state.report_text = read_weekly_template("_mau-tuan.md") if report_format == "Weekly journal" else make_report(jobs, issues)
    with st.container(border=True):
        top_left, top_right = st.columns([2, 1])
        with top_left:
            st.markdown(f"**Status:** <span class='status-pill {'status-good' if st.session_state.report_status == 'Approved' else 'status-warn'}'>{st.session_state.report_status}</span>", unsafe_allow_html=True)
        with top_right:
            if st.button("↻ Generate from current data", width="stretch"):
                st.session_state.report_text = make_weekly_report(jobs, issues, "Week 01") if report_format == "Weekly journal" else make_report(jobs, issues)
                st.session_state.report_status = "Draft"
                st.rerun()
        if report_format == "Weekly journal":
            st.caption("Ô soạn thảo dùng `_mau-tuan.md`; `tuan-01.md` chỉ là ví dụ tham khảo ở chế độ đọc.")
            load_col, example_col = st.columns([1, 1])
            with load_col:
                if st.button("Load blank weekly template", width="stretch"):
                    st.session_state.report_text = read_weekly_template("_mau-tuan.md")
                    st.session_state.report_status = "Draft"
                    st.rerun()
            with example_col:
                show_example = st.checkbox("Read-only example", value=False)
        else:
            show_example = False

        report_name = st.text_input("Export file name", value="weekly-report-week-01" if report_format == "Weekly journal" else "mentor-report", help="Không cần nhập phần mở rộng .md hoặc .docx.")
        if show_example:
            editor_col, example_col = st.columns(2, gap="large")
            with editor_col:
                st.markdown("### Edit report")
                st.session_state.report_text = st.text_area("Edit report", value=st.session_state.report_text, height=620, label_visibility="collapsed")
            with example_col:
                st.markdown("### Read-only example")
                example_text = html.escape(read_weekly_template("tuan-01.md"))
                st.markdown(f'<div class="readonly-example"><pre>{example_text}</pre></div>', unsafe_allow_html=True)
        else:
            st.session_state.report_text = st.text_area("Edit report", value=st.session_state.report_text, height=510, label_visibility="collapsed")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Save draft", width="stretch"):
                st.session_state.report_status = "Draft"
                st.success("Draft saved in this session.")
        with c2:
            if st.button("Approve report", type="primary", width="stretch"):
                st.session_state.report_status = "Approved"
                st.success("Report approved.")
        with c3:
            st.download_button("Download Markdown", st.session_state.report_text, file_name=safe_download_name(report_name, ".md"), mime="text/markdown", width="stretch")
        st.download_button("Download DOCX", report_to_docx(st.session_state.report_text), file_name=safe_download_name(report_name, ".docx"), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch")


def assistant_page(category: str, week: str) -> None:
    st.markdown('<div class="eyebrow">Guideline-backed assistant</div>', unsafe_allow_html=True)
    st.title("Annotation Assistant")
    st.caption("This assistant answers from the selected guideline only. No supporting source means mentor review.")
    left, right = st.columns([1.45, 1])
    with left:
        question = st.text_area("Your annotation question", placeholder="Ví dụ: Khi object bị che khuất toàn phần, có giữ track ID không?", height=120)
        ask = st.button("Ask guideline", type="primary", width="stretch")
        if ask and question.strip():
            sources = filtered_guidelines(week, category, question)
            answer, status = build_answer(question, sources)
            record = {"question": question, "answer": answer, "status": status, "sources": sources[:2], "time": datetime.now().strftime("%H:%M")}
            st.session_state.qa_history.insert(0, record)
            if status == "needs_review":
                st.session_state.mentor_queue.append(record)
        elif ask:
            st.warning("Hãy nhập câu hỏi trước khi gửi.")
        if st.session_state.qa_history:
            st.markdown("### Latest answer")
            item = st.session_state.qa_history[0]
            pill = "status-good" if item["status"] == "answered" else "status-warn"
            st.markdown(f'<span class="status-pill {pill}">{item["status"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-card"><h3>Answer</h3><p>{item["answer"].replace(chr(10), "<br>")}</p></div>', unsafe_allow_html=True)
            if item["sources"]:
                st.markdown("#### Sources")
                for source in item["sources"]:
                    st.markdown(f'<div class="source-card"><strong>{source["doc"]}</strong> · {source["version"]}<br><span class="small-muted">{source["week"]} · {source["category"]} · {source["section"]} · {source["page"]}</span></div>', unsafe_allow_html=True)
    with right:
        st.markdown("#### Context")
        st.info(f"Week: {week}\n\nCategory: {category}")
        st.markdown("#### Mentor queue")
        if st.session_state.mentor_queue:
            st.warning(f"{len(st.session_state.mentor_queue)} question(s) need mentor review.")
            for idx, item in enumerate(st.session_state.mentor_queue):
                with st.expander(f"{item['time']} · {item['question'][:42]}"):
                    st.write(item["answer"])
                    if st.button("Mark resolved", key=f"resolve_{idx}"):
                        st.session_state.mentor_queue.pop(idx)
                        st.rerun()
        else:
            st.success("No pending mentor questions.")
        st.markdown("#### Guideline library")
        st.caption(f"{len(st.session_state.guidelines)} chunks available in this workspace")
        with st.expander("Upload guideline"):
            uploaded = st.file_uploader("File (.md or .txt)", type=["md", "txt"])
            upload_doc = st.text_input("Document name", value=uploaded.name if uploaded else "")
            upload_version = st.text_input("Version", value="uploaded")
            upload_week = st.selectbox("Applies to week", [w for w in sorted({g["week"] for g in st.session_state.guidelines})], key="upload_week")
            upload_category = st.selectbox("Applies to category", [c for c in sorted({g["category"] for g in st.session_state.guidelines})], key="upload_category")
            if uploaded is not None and st.button("Add to library"):
                raw = uploaded.getvalue().decode("utf-8", errors="ignore")
                st.session_state.guidelines.append({"doc": upload_doc or uploaded.name, "version": upload_version, "week": upload_week, "category": upload_category, "section": "Uploaded content", "page": "—", "text": raw[:5000]})
                st.success("Guideline added to the current session.")


def main() -> None:
    init_state()
    batch, category, week = render_sidebar()
    if st.button("☰", key="sidebar_toggle", help="Thu/mở thanh tùy chọn"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()
    jobs = filtered_jobs(batch, category)
    issues = [i for i in ISSUES if (category == "All categories" or i["category"] == category)]
    page = st.radio("Navigation", ["Dashboard", "Report studio", "Annotation Assistant"], horizontal=True, label_visibility="collapsed")
    if page == "Dashboard":
        dashboard_page(jobs, issues)
    elif page == "Report studio":
        report_page(jobs, issues)
    else:
        assistant_page(category, week)


if __name__ == "__main__":
    main()
