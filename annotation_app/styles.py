from __future__ import annotations

import streamlit as st


def apply_styles(sidebar_open: bool) -> None:
    nav_left = "272px" if sidebar_open else "62px"
    collapsed = "" if sidebar_open else """
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
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    """
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root {{ --ink:#17212b; --muted:#70808f; --line:#e5e9ee; --navy:#132b43; --mint:#36a995; }}
        html, body, [class*="css"] {{ font-family:'DM Sans', sans-serif; color:var(--ink); }}
        h1,h2,h3,h4 {{ font-family:'Space Grotesk', sans-serif; letter-spacing:-.02em; }}
        .block-container {{ padding-top:5.8rem !important; max-width:1440px; }}
        [data-testid="stSidebar"] {{ background:#101a2b; border-right:1px solid #26364a; color:#edf4fb; }}
        [data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{ color:#edf4fb !important; }}
        [data-testid="stSidebarCollapsedControl"] {{ display:none !important; }}
        span[data-testid="stTooltipIcon"]:has(button p) {{ position:fixed !important; left:8px !important; top:12px !important; z-index:999999 !important; }}
        span[data-testid="stTooltipIcon"]:has(button p) button {{ min-width:44px !important; width:44px !important; height:44px !important; padding:0 !important; border-radius:8px !important; background:#1e293b !important; border:1px solid #52657d !important; color:#f8fafc !important; }}
        [data-testid="stMetric"] {{ background:white; border:1px solid var(--line); padding:16px 18px; border-radius:14px; }}
        [data-testid="stMetricValue"] {{ font-family:'Space Grotesk', sans-serif; font-size:1.65rem; }}
        .hero {{ background:linear-gradient(120deg,#102940 0%,#1e4565 70%,#286e78 100%); color:white; border-radius:20px; padding:28px 32px; margin-bottom:24px; }}
        .hero h1 {{ color:white; margin:0 0 8px 0; font-size:2.2rem; }} .hero p {{ color:#cfe0ed; margin:0; max-width:700px; font-size:1rem; }}
        .eyebrow {{ text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; color:#89c9c0; margin-bottom:8px; }}
        .small-muted {{ color:var(--muted); font-size:.86rem; }}
        .status-pill {{ display:inline-block; border-radius:20px; padding:4px 10px; font-size:.76rem; font-weight:700; }}
        .status-good {{ background:#e4f5ef; color:#187d68; }} .status-warn {{ background:#fff2d9; color:#9d6811; }} .status-danger {{ background:#fde8e8; color:#aa4047; }}
        .source-card {{ border:1px solid var(--line); border-radius:12px; padding:13px 15px; background:white; margin:6px 0; }} .source-card strong {{ color:var(--navy); }}
        .report-card {{ background:white; border:1px solid var(--line); border-radius:16px; padding:22px 24px; }} .report-card h3 {{ margin-top:0; color:var(--navy); }}
        .readonly-example {{ height:620px; overflow:auto; background:#20232d; color:#f1f3f5; border:1px solid #3a4050; border-radius:8px; padding:14px 16px; font-family:'Cascadia Mono','Consolas',monospace; font-size:.82rem; line-height:1.45; white-space:pre-wrap; }} .readonly-example pre {{ margin:0; font:inherit; white-space:pre-wrap; }}
        .login-shell {{ background:#fff; border:1px solid var(--line); border-radius:20px; padding:28px; box-shadow:0 18px 50px rgba(19,43,67,.08); margin-top:8vh; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) {{ position:fixed !important; top:0 !important; left:{nav_left} !important; right:0 !important; z-index:1000001 !important; padding:12px 24px 10px !important; background:#0b111a !important; border-bottom:1px solid #26364a !important; box-shadow:0 4px 16px rgba(0,0,0,.18) !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioGroup"] {{ gap:0 !important; align-items:stretch !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] {{ min-height:38px !important; padding:10px 16px !important; border-radius:0 !important; color:#e7edf5 !important; cursor:pointer !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] > div > div:first-child {{ display:none !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] > div {{ gap:0 !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioOption"] p {{ margin:0 !important; color:inherit !important; font-size:.95rem !important; white-space:nowrap !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Navigation"]) [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {{ background:#f2a65a !important; color:#17212b !important; font-weight:700 !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) {{ background:#111d2d !important; border:1px solid #33465e !important; border-radius:14px !important; padding:10px 12px !important; margin:8px 0 18px !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioGroup"] {{ gap:0 !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] {{ min-height:38px !important; padding:10px 22px !important; border-radius:0 !important; color:#e7edf5 !important; cursor:pointer !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] > div > div:first-child {{ display:none !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] > div {{ gap:0 !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioOption"] p {{ margin:0 !important; color:inherit !important; white-space:nowrap !important; }}
        div[data-testid="stRadio"]:has([role="radiogroup"][aria-label="Report format"]) [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {{ background:#f2a65a !important; color:#17212b !important; font-weight:700 !important; }}
        {collapsed}
        </style>
        """,
        unsafe_allow_html=True,
    )
