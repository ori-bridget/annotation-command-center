from __future__ import annotations

import streamlit as st

from annotation_app.auth import current_user, init_auth, render_login
from annotation_app.data import GUIDELINES, filtered_issues, filtered_jobs
from annotation_app.pages import assistant_page, dashboard_page, report_page
from annotation_app.sidebar import render_navigation, render_sidebar
from annotation_app.styles import apply_styles


st.set_page_config(
    page_title="Annotation Command Center",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="auto",
)


def init_workspace() -> None:
    st.session_state.setdefault("guidelines", list(GUIDELINES))
    st.session_state.setdefault("report_text", "")
    st.session_state.setdefault("report_status", "Draft")
    st.session_state.setdefault("report_format", None)
    st.session_state.setdefault("mentor_queue", [])
    st.session_state.setdefault("qa_history", [])
    st.session_state.setdefault("sidebar_open", True)


def main() -> None:
    init_auth()
    init_workspace()
    user = current_user()
    if user is None:
        apply_styles(True)
        render_login()
        return

    apply_styles(st.session_state.sidebar_open)
    batch, category, week = render_sidebar(user)
    if st.button("☰", key="sidebar_toggle", help="Thu/mở thanh tùy chọn"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

    page = render_navigation()
    jobs = filtered_jobs(batch, category)
    issues = filtered_issues(category)
    if page == "Dashboard":
        dashboard_page(jobs, issues)
    elif page == "Report studio":
        report_page(jobs, issues, user)
    else:
        assistant_page(category, week, user)


if __name__ == "__main__":
    main()
