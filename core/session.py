import streamlit as st
import time
from core.constants import UIConstants

class SessionManager:
    @staticmethod
    def init_session():
        if 'last_action_time' not in st.session_state:
            st.session_state.last_action_time = time.time()
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0

    @staticmethod
    def update_activity():
        st.session_state.last_action_time = time.time()

    @staticmethod
    def check_timeout():
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            elapsed = (time.time() - st.session_state.last_action_time) / 60
            if elapsed > UIConstants.SESSION_TIMEOUT:
                from services.auth_service import AuthService
                AuthService.logout()
                st.error("Oturumunuz uzun süre işlem yapılmadığı için kapatıldı.")
                st.rerun()

    @staticmethod
    def record_failed_login():
        st.session_state.login_attempts += 1
        if st.session_state.login_attempts >= 5:
            st.error("Çok fazla hatalı giriş denemesi. Lütfen sistem yöneticisi ile iletişime geçin.")
            return False
        return True

    @staticmethod
    def reset_login_attempts():
        st.session_state.login_attempts = 0

    @staticmethod
    def require_role(roles):
        if 'role' not in st.session_state or st.session_state.role not in roles:
            st.warning("Bu işlemi yapmak için yetkiniz bulunmuyor.")
            st.stop()
