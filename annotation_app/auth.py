from __future__ import annotations

import streamlit as st


DEMO_USERS = {
    "mentor": {"password": "mentor123", "role": "mentor", "display_name": "Mentor Demo"},
    "lead": {"password": "lead123", "role": "lead", "display_name": "Lead Demo"},
    "member": {"password": "member123", "role": "member", "display_name": "Member Demo"},
}

ROLE_LABELS = {"mentor": "Mentor", "lead": "Lead", "member": "Member"}


def init_auth() -> None:
    st.session_state.setdefault("authenticated_user", None)


def current_user() -> dict | None:
    username = st.session_state.get("authenticated_user")
    if not username or username not in DEMO_USERS:
        return None
    account = DEMO_USERS[username]
    return {"username": username, **account}


def can_approve_report(role: str) -> bool:
    return role in {"mentor", "lead"}


def can_resolve_mentor_queue(role: str) -> bool:
    return role == "mentor"


def render_login() -> None:
    left, center, right = st.columns([1, 1.1, 1])
    with center:
        st.markdown('<div class="login-shell">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">Annotation OS</div>', unsafe_allow_html=True)
        st.title("Sign in")
        st.caption("Đăng nhập theo vai trò để mở workspace.")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="mentor, lead hoặc member")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            account = DEMO_USERS.get(username.strip().lower())
            if account and password == account["password"]:
                st.session_state.authenticated_user = username.strip().lower()
                st.rerun()
            st.error("Sai username hoặc password.")
        st.info("Demo accounts: mentor / mentor123 · lead / lead123 · member / member123")
        st.markdown('</div>', unsafe_allow_html=True)


def render_user_menu(user: dict) -> None:
    st.markdown(f"**{user['display_name']}**")
    st.caption(f"Role · {ROLE_LABELS[user['role']]}")
    if st.button("Sign out", key="sign_out", use_container_width=True):
        st.session_state.authenticated_user = None
        st.rerun()
