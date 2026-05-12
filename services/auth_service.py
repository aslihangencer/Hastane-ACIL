import streamlit as st
from core.stitch import db

class AuthService:
    @staticmethod
    def init_session():
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.auth_type = None
            st.session_state.role = None
            st.session_state.login_view = None

    @staticmethod
    def login_hasta(tc, h_id):
        query = "SELECT * FROM dbo.HASTA WHERE TCKimlikNo = ? AND HastaID = ?"
        patient = db.fetch(query, (tc, h_id))
        if not patient.empty:
            st.session_state.authenticated = True
            st.session_state.user = patient.iloc[0].to_dict()
            st.session_state.auth_type = 'hasta'
            st.session_state.user_id = patient.iloc[0]['HastaID']
            st.session_state.role = 'Patient'
            return True
        st.error("TC veya Hasta ID hatalı.")
        return False

    @staticmethod
    def login_personel(username, password):
        # FIX: Using LEFT JOIN because some users (like 'admin') might not have a PersonelID linked.
        # Also using correct column names (KullaniciAdi, SifreHash).
        query = """
        SELECT K.KullaniciID, K.KullaniciAdi, K.Rol AS SistemRol, P.* 
        FROM dbo.KULLANICILAR K
        LEFT JOIN dbo.PERSONEL P ON K.PersonelID = P.PersonelID
        WHERE K.KullaniciAdi = ? AND K.SifreHash = ?
        """
        user = db.fetch(query, (username, password))
        if not user.empty:
            st.session_state.authenticated = True
            user_data = user.iloc[0].to_dict()
            st.session_state.user = user_data
            st.session_state.auth_type = 'personel'
            st.session_state.user_id = user_data.get('PersonelID') or user_data.get('KullaniciID')
            # Priority: Personnel Role -> User Table Role -> Default
            st.session_state.role = user_data.get('Rol') or user_data.get('SistemRol') or 'Admin'
            return True
        st.error("Kullanıcı adı veya şifre hatalı.")
        return False

    @staticmethod
    def logout():
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.auth_type = None
        st.session_state.role = None
        st.session_state.login_view = None
        st.rerun()

    @staticmethod
    def is_authenticated():
        return st.session_state.get('authenticated', False)
