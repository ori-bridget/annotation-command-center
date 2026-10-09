from __future__ import annotations

import html
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

from .auth import ROLE_LABELS, can_approve_report, can_resolve_mentor_queue
from .data import filtered_guidelines
from .services import build_answer, make_report, make_weekly_report, read_template, report_to_docx, safe_download_name


def dashboard_page(jobs: list[dict], issues: list[dict]) -> None:
    st.markdown('<div class="eyebrow">Mentor preparation workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Build clarity before the mentor session.</h1><p>The command center for progress, quality signals, open questions and guideline-backed answers.</p></div>', unsafe_allow_html=True)
    total = len(jobs)
    completed = sum(job["status"] == "Completed" for job in jobs)
    avg_score = round(sum(job["score"] for job in jobs) / total, 1) if total else 0
    open_issues = sum(issue["status"] == "Open" for issue in issues)
    hard = sum(job["hard"] for job in jobs)
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
            chart = alt.Chart(status_counts).mark_bar(color="#36a995", cornerRadiusEnd=5).encode(
                x=alt.X("Jobs:Q", scale=alt.Scale(domainMin=0), axis=alt.Axis(title=None, format="d")),
                y=alt.Y("Status:N", sort="-x", axis=alt.Axis(title=None, labelLimit=180)),
                tooltip=[alt.Tooltip("Status:N", title="Trạng thái"), alt.Tooltip("Jobs:Q", title="Số lượng job", format="d")],
            ).properties(height=240)
            st.altair_chart(chart, width="stretch")
    with right:
        st.markdown("#### Data sources")
        st.markdown(f'<div class="source-card"><strong>CVAT</strong><br><span class="small-muted">{len(jobs)} selected jobs · synced successfully</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="source-card"><strong>GitHub</strong><br><span class="small-muted">{len(issues)} filtered issues · {open_issues} open</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="source-card"><strong>Guidelines</strong><br><span class="small-muted">{len(st.session_state.guidelines)} chunks · {len({g["category"] for g in st.session_state.guidelines})} categories</span></div>', unsafe_allow_html=True)

    st.markdown("### Quality signals")
    left, right = st.columns([1.15, 1])
    with left:
        hard_rows = [job for job in jobs if job["hard"]]
        if hard_rows:
            hard_df = pd.DataFrame(hard_rows)[["job_id", "category", "assignee", "score", "edits", "age"]]
            hard_df.columns = ["Job", "Category", "Assignee", "Score", "Edits", "Age (days)"]
            st.dataframe(hard_df, hide_index=True, width="stretch")
        else:
            st.success("No hard cases in the current filter.")
    with right:
        for issue in [item for item in issues if item["status"] == "Open"]:
            st.markdown(f'<div class="source-card"><span class="status-pill status-warn">{issue["id"]}</span> <strong>{issue["title"]}</strong><br><span class="small-muted">{issue["job_id"]} · {issue["category"]}</span></div>', unsafe_allow_html=True)

    st.markdown("### Job detail")
    table = pd.DataFrame(jobs)
    if not table.empty:
        table = table[["job_id", "category", "assignee", "status", "score", "edits"]]
        table.columns = ["Job", "Category", "Assignee", "Status", "Score", "Edits"]
        st.dataframe(table, hide_index=True, width="stretch")


def report_page(jobs: list[dict], issues: list[dict], user: dict) -> None:
    st.markdown('<div class="eyebrow">Report studio</div>', unsafe_allow_html=True)
    st.title("Mentor report")
    st.caption(f"Signed in as {user['display_name']} · {ROLE_LABELS[user['role']]}. Numbers are computed from the filtered dataset.")
    report_format = st.radio("Report format", ["Weekly journal", "Mentor report · 4 sections"], horizontal=True)
    if st.session_state.get("report_format") != report_format:
        st.session_state.report_format = report_format
        st.session_state.report_text = read_template("_mau-tuan.md") if report_format == "Weekly journal" else make_report(jobs, issues)
    if not st.session_state.report_text:
        st.session_state.report_text = read_template("_mau-tuan.md") if report_format == "Weekly journal" else make_report(jobs, issues)

    with st.container(border=True):
        top_left, top_right = st.columns([2, 1])
        with top_left:
            status_class = "status-good" if st.session_state.report_status == "Approved" else "status-warn"
            st.markdown(f"**Status:** <span class='status-pill {status_class}'>{st.session_state.report_status}</span>", unsafe_allow_html=True)
        with top_right:
            if st.button("↻ Generate from current data", width="stretch"):
                st.session_state.report_text = make_weekly_report(jobs, issues, "Week 01") if report_format == "Weekly journal" else make_report(jobs, issues)
                st.session_state.report_status = "Draft"
                st.rerun()
        if report_format == "Weekly journal":
            st.caption("Ô soạn thảo dùng `_mau-tuan.md`; `tuan-01.md` là ví dụ tham khảo ở chế độ đọc.")
            load_col, example_col = st.columns([1, 1])
            with load_col:
                if st.button("Load blank weekly template", width="stretch"):
                    st.session_state.report_text = read_template("_mau-tuan.md")
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
                st.markdown(f'<div class="readonly-example"><pre>{html.escape(read_template("tuan-01.md"))}</pre></div>', unsafe_allow_html=True)
        else:
            st.session_state.report_text = st.text_area("Edit report", value=st.session_state.report_text, height=510, label_visibility="collapsed")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Save draft", width="stretch"):
                st.session_state.report_status = "Draft"
                st.success("Draft saved in this session.")
        with c2:
            if can_approve_report(user["role"]):
                if st.button("Approve report", type="primary", width="stretch"):
                    st.session_state.report_status = "Approved"
                    st.success("Report approved.")
            else:
                st.caption("Only Lead or Mentor can approve.")
        with c3:
            st.download_button("Download Markdown", st.session_state.report_text, file_name=safe_download_name(report_name, ".md"), mime="text/markdown", width="stretch")
        st.download_button("Download DOCX", report_to_docx(st.session_state.report_text), file_name=safe_download_name(report_name, ".docx"), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch")


def assistant_page(category: str, week: str, user: dict) -> None:
    st.markdown('<div class="eyebrow">Guideline-backed assistant</div>', unsafe_allow_html=True)
    st.title("Annotation Assistant")
    st.caption("This assistant answers from the selected guideline only. No supporting source means mentor review.")
    left, right = st.columns([1.45, 1])
    with left:
        question = st.text_area("Your annotation question", placeholder="Ví dụ: Khi object bị che khuất toàn phần, có giữ track ID không?", height=120)
        ask = st.button("Ask guideline", type="primary", width="stretch")
        if ask and question.strip():
            sources = filtered_guidelines(st.session_state.guidelines, week, category, question)
            answer, status = build_answer(question, sources)
            record = {"question": question, "answer": answer, "status": status, "sources": sources[:2], "time": datetime.now().strftime("%H:%M")}
            st.session_state.qa_history.insert(0, record)
            if status == "needs_review":
                st.session_state.mentor_queue.append(record)
        elif ask:
            st.warning("Hãy nhập câu hỏi trước khi gửi.")
        if st.session_state.qa_history:
            item = st.session_state.qa_history[0]
            st.markdown("### Latest answer")
            st.markdown(f'<span class="status-pill {"status-good" if item["status"] == "answered" else "status-warn"}">{item["status"]}</span>', unsafe_allow_html=True)
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
                    if can_resolve_mentor_queue(user["role"]):
                        if st.button("Mark resolved", key=f"resolve_{idx}"):
                            st.session_state.mentor_queue.pop(idx)
                            st.rerun()
                    else:
                        st.caption("Chỉ Mentor mới có thể đóng mentor queue.")
        else:
            st.success("No pending mentor questions.")
        st.markdown("#### Guideline library")
        st.caption(f"{len(st.session_state.guidelines)} chunks available in this workspace")
        with st.expander("Upload guideline"):
            uploaded = st.file_uploader("File (.md or .txt)", type=["md", "txt"])
            upload_doc = st.text_input("Document name", value=uploaded.name if uploaded else "")
            upload_version = st.text_input("Version", value="uploaded")
            weeks = sorted({item["week"] for item in st.session_state.guidelines})
            categories = sorted({item["category"] for item in st.session_state.guidelines})
            upload_week = st.selectbox("Applies to week", weeks, key="upload_week")
            upload_category = st.selectbox("Applies to category", categories, key="upload_category")
            if uploaded is not None and st.button("Add to library"):
                raw = uploaded.getvalue().decode("utf-8", errors="ignore")
                st.session_state.guidelines.append({"doc": upload_doc or uploaded.name, "version": upload_version, "week": upload_week, "category": upload_category, "section": "Uploaded content", "page": "—", "text": raw[:5000]})
                st.success("Guideline added to the current session.")
