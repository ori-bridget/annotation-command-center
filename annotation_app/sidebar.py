from __future__ import annotations

import streamlit as st

from .auth import render_user_menu
from .data import JOBS


def render_sidebar(user: dict) -> tuple[str, str, str]:
    with st.sidebar:
        st.markdown("### ◆ Annotation OS")
        st.caption("MVP · Report + Guideline Assistant")
        render_user_menu(user)
        st.caption("☰ Dùng nút ở đầu trang để thu/mở thanh tùy chọn")
        st.divider()
        st.markdown("**Workspace**")
        st.selectbox("Nguồn dữ liệu", ["Demo workspace", "CVAT + GitHub (sắp kết nối)"], label_visibility="collapsed")
        batches = ["All batches"] + sorted({job["batch"] for job in JOBS})
        categories = ["All categories"] + sorted({job["category"] for job in JOBS})
        weeks = ["All weeks"] + sorted({item["week"] for item in st.session_state.guidelines})
        batch = st.selectbox("Batch", batches)
        category = st.selectbox("Job category", categories)
        week = st.selectbox("Guideline week", weeks)
    return batch, category, week


def render_navigation() -> str:
    return st.radio("Navigation", ["Dashboard", "Report studio", "Annotation Assistant"], horizontal=True, label_visibility="collapsed")
