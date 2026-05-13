import sys
import os
# Proje kök dizinini sisteme ekliyoruz ki importlar düzgün çalışsın
sys.path.append(os.getcwd())

import streamlit as st
from core.config import Config
from core.theme import inject_premium_css
from core.bootloader import Bootloader
from services.auth_service import AuthService
from ui.pages.patient_portal import render_patient_portal
from ui.pages.staff_dashboard import render_staff_dashboard

# ==========================================
# 🧱 SİSTEM BAŞLATMA VE HATA KONTROLÜ
# ==========================================
# Uygulama ilk kez çalışırken gerekli ayarları ve veritabanı bağlantısını kontrol ediyoruz
if 'boot_ready' not in st.session_state:
    with st.spinner("Sistem Hazırlanıyor..."):
        is_ready = Bootloader.run_safe_boot()
        st.session_state['boot_ready'] = is_ready

# Eğer sistem düzgün başlatılamadıysa bakım ekranını gösteriyoruz
if not st.session_state['boot_ready']:
    Bootloader.render_maintenance_ui()

# ==========================================
# 🏥 ANA UYGULAMA AKIŞI
# ==========================================

# Tarayıcı sekmesi ayarları
st.set_page_config(
    page_title="Hastane Acil Servis", 
    page_icon="🏥", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Görsel tasarım (CSS) enjeksiyonu
inject_premium_css()

# Oturum yönetimi başlatma
AuthService.init_session()

# Sayfa genelinde kullanılan değişkenlerin (yatak seçimi vb.) ön tanımlaması
if 'selected_bed' not in st.session_state or st.session_state.selected_bed is None:
    st.session_state.selected_bed = {}

# Tasarımda kullanılan ikon yolları
DOCTOR_ICON = "C:/Users/Handan Gencer/.gemini/antigravity/brain/a80efca0-1516-4ecd-afb9-6e6a78b3e63c/doctor_icon_3d_1778328405892.png"
PATIENT_ICON = "C:/Users/Handan Gencer/.gemini/antigravity/brain/a80efca0-1516-4ecd-afb9-6e6a78b3e63c/patient_icon_3d_1778328390452.png"

# --- GİRİŞ EKRANLARI ---

# Kullanıcının Hasta mı yoksa Personel mi olduğunu seçtiği ana ekran
def render_login_selection():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1e3a5f; font-size: 2.8rem; margin-bottom: 0;'>HASTANE ACİL SERVİS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1rem;'>Kurumsal Acil Otomasyon Sistemi</p><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col2:
        st.image(PATIENT_ICON, width=350)
        st.markdown("<h2 style='color:#1e3a5f; margin-top:10px; text-align:center;'>Hasta Portalı</h2>", unsafe_allow_html=True)
        if st.button("Sisteme Giriş Yap", key="btn-hasta", use_container_width=True):
            st.session_state.login_view = 'hasta'
            st.rerun()
            
    with col3:
        st.image(DOCTOR_ICON, width=350)
        st.markdown("<h2 style='color:#1e3a5f; margin-top:10px; text-align:center;'>Personel Girişi</h2>", unsafe_allow_html=True)
        if st.button("Sisteme Giriş Yap", key="btn-personel", use_container_width=True, type="primary"):
            st.session_state.login_view = 'personel'
            st.rerun()

# Hastaların TC No ve ID ile giriş yaptığı ekran
def render_hasta_login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#1e3a5f; text-align:center;'>👤 Hasta Giriş Paneli</h2>", unsafe_allow_html=True)
        with st.form("hasta_login"):
            tc = st.text_input("TC Kimlik No")
            h_id = st.text_input("Hasta ID")
            if st.form_submit_button("Sisteme Giriş", type="primary", use_container_width=True):
                if AuthService.login_hasta(tc, h_id): st.rerun()
        
        st.markdown("""
            <div style='background: #fffbeb; padding: 20px; border-radius: 12px; border: 2px solid #fde68a; margin-top: 25px;'>
                <p style='color: #92400e; font-size: 0.9rem; margin: 0; line-height: 1.5;'>
                    ⚠️ <b>Kritik Bilgilendirme:</b><br>
                    Sistemde kaydı bulunmayan hastaların işlem yapabilmesi için öncelikle hastane kayıt biriminden <b>Hasta ID</b> tanımlatması zorunludur.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("← Geri Dön", use_container_width=True):
            st.session_state.login_view = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Hastane personelinin giriş yaptığı ekran
def render_personel_login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#1e3a5f; text-align:center;'>🏥 Personel Giriş Paneli</h2>", unsafe_allow_html=True)
        with st.form("personel_login"):
            k_adi = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            if st.form_submit_button("Sisteme Giriş", type="primary", use_container_width=True):
                if AuthService.login_personel(k_adi, sifre): st.rerun()
        
        st.markdown("""
            <div style='background: #f0f9ff; padding: 20px; border-radius: 12px; border: 2px solid #bae6fd; margin-top: 25px;'>
                <p style='color: #0369a1; font-size: 0.9rem; margin: 0; line-height: 1.5;'>
                    ℹ️ <b>Personel Bilgilendirme:</b><br>
                    Sisteme giriş yapabilmek için BT birimi tarafından tanımlanmış <b>Kurumsal Kullanıcı</b> hesabınızın olması gerekmektedir.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("← Geri Dön", use_container_width=True):
            st.session_state.login_view = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Ana yönlendirme fonksiyonu (Authentication durumuna göre ekran seçer)
def main():
    if not AuthService.is_authenticated():
        # Giriş yapılmadıysa login ekranlarını göster
        view = st.session_state.get('login_view')
        if view == 'hasta': render_hasta_login()
        elif view == 'personel': render_personel_login()
        else: render_login_selection()
    else:
        # Giriş yapıldıysa yetkiye göre portalı aç
        if st.session_state.auth_type == 'hasta':
            render_patient_portal()
        else:
            render_staff_dashboard()

if __name__ == "__main__":
    main()
