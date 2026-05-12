import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from core.constants import UIConstants
from services.notification_service import NotificationService

def render_top_navbar():
    st.markdown(f"""
        <div class="top-navbar">
            <div style="display:flex; align-items:center; gap:15px;">
                <span style="font-size:1.5rem;">🏥</span>
                <span style="font-weight:700; color:#1e3a5f; font-size:1.1rem;">ACİL SERVİS ERP <span style="font-size:0.7rem; color:#64748b; font-weight:400;">v{UIConstants.VERSION}</span></span>
            </div>
            <div style="display:flex; align-items:center; gap:20px;">
                <div style="color:#64748b; font-size:0.85rem; display:flex; align-items:center; gap:5px;">
                    🔍 <input type="text" placeholder="Hasta / Oda / Doktor Ara..." style="border:none; background:transparent; font-size:0.85rem; width:180px; outline:none;">
                </div>
            </div>
        </div>
        <div style="margin-top: 70px;"></div>
    """, unsafe_allow_html=True)

def render_system_footer():
    now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
        <div class="system-footer">
            <div>🟢 Veritabanı Bağlı: <b>HastaneAcilServis</b></div>
            <div>⚡ Son Güncelleme: {now} | Oturum Süresi: {UIConstants.SESSION_TIMEOUT} dk</div>
            <div>© 2026 Meditech Style ERP Systems</div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar_profile():
    user = st.session_state.get('user', {})
    role = st.session_state.get('role', 'Misafir')
    
    st.sidebar.markdown(f"""
        <div style='text-align: center; padding: 10px 0;'>
            <div style='font-size: 3rem;'>👤</div>
            <div style='font-weight: 700; color: #1e3a5f; font-size: 1rem;'>{user.get('Ad') if user.get('Ad') else 'Sistem'} {user.get('Soyad') if user.get('Soyad') else 'Yöneticisi'}</div>
            <div style='font-size: 0.8rem; color: #64748b;'>{role} | ID: {user.get('PersonelID') or user.get('KullaniciID', '---')}</div>
        </div>
        <hr style='margin: 10px 0;'>
    """, unsafe_allow_html=True)
    
    NotificationService.render_notification_hub()
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
