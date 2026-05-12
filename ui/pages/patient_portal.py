import streamlit as st
import pandas as pd
import plotly.express as px
from data.read_repository import get_patient_timeline, get_visit_count, get_patient_lab_results, normalize_gender
from ui.components.timeline import render_timeline
from services.auth_service import AuthService

def render_patient_portal():
    user = st.session_state.user
    hasta_id = user.get('HastaID')
    
    # Professional Gender Mapping
    gender_label = normalize_gender(user.get('Cinsiyet'))
    
    # Blood Type (Real from DB)
    blood_type = user.get('KanGrubu', 'Belirtilmemiş')
    
    # 1. Sidebar Patient Card
    with st.sidebar:
        st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
                <div style='font-size: 3rem; text-align:center;'>👤</div>
                <h3 style='text-align:center; color:#1e3a5f; margin:10px 0;'>{user.get('Ad')} {user.get('Soyad')}</h3>
                <hr>
                <p>🆔 <b>Hasta ID:</b> {hasta_id}</p>
                <p>🎂 <b>Yaş:</b> {user.get('Yas')}</p>
                <p>🧬 <b>Cinsiyet:</b> {gender_label}</p>
                <p>🩸 <b>Kan Grubu:</b> <span style='color:#ef4444; font-weight:bold;'>{blood_type}</span></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            AuthService.logout()

    # 2. Main Header
    st.markdown(f"<h1 style='color:#1e3a5f;'>Hasta İşlem Merkezi</h1>", unsafe_allow_html=True)
    st.info(f"Sistemdeki {get_visit_count(hasta_id)}. ziyaretiniz. Geçmiş kayıtlarınızı aşağıdan inceleyebilirsiniz.")

    # 3. Tabs
    tab1, tab2 = st.tabs(["🕒 Klinik Geçmiş", "🧪 Laboratuvar Sonuçları"])
    
    with tab1:
        st.markdown("<div class='premium-card'><div class='card-title'>🕒 Klinik Zaman Akışı (Taburcu Kayıtları)</div>", unsafe_allow_html=True)
        timeline_data = get_patient_timeline(hasta_id)
        
        # SAFE DATAFRAME CHECK (Crash-Proof)
        if timeline_data is not None and not timeline_data.empty:
            render_timeline(timeline_data)
        else:
            st.info("Klinik kaydınız henüz işlenmedi.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='premium-card'><div class='card-title'>🧬 Laboratuvar Bulguları</div>", unsafe_allow_html=True)
        lab_data = get_patient_lab_results(hasta_id)
        
        # SAFE DATAFRAME CHECK (Crash-Proof)
        if lab_data is not None and not lab_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**CRP Trendi**")
                fig_crp = px.line(lab_data, x='Tarih', y='CRP', markers=True, color_discrete_sequence=['#ef4444'])
                st.plotly_chart(fig_crp, use_container_width=True)
            with col2:
                st.markdown("**WBC Sayımı**")
                fig_wbc = px.bar(lab_data, x='Tarih', y='WBC', color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig_wbc, use_container_width=True)
        else:
            st.info("Onaylanmış sonuç bulunmamaktadır.")
        st.markdown("</div>", unsafe_allow_html=True)
