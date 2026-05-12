import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def render_patient_sidebar(patient_data, visit_count=0):
    """Renders the professional patient info card in the sidebar."""
    st.markdown("### 👤 Hasta Bilgileri")
    
    # Recurring Patient Badge
    badge_html = ""
    if visit_count > 1:
        badge_html = f"""
        <div style="background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-bottom: 10px; border: 1px solid #ef4444; text-align: center;">
            ⚠️ TEKRAR EDEN HASTA ({visit_count}. Başvuru)
        </div>
        """
    
    # Premium Profile Header
    st.markdown(f"""
    {badge_html}
    <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e2e8f0;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
            <div style="background: #eff6ff; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; border: 2px solid #3b82f6;">👤</div>
            <div>
                <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Ad Soyad</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #1e293b;">{patient_data.get('Ad', '')} {patient_data.get('Soyad', '')}</div>
            </div>
        </div>
        <div style="font-size: 14px; line-height: 2;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0;">
                <span style="color: #64748b;">T.C. Kimlik:</span>
                <span style="font-weight: 600; color: #334155;">{patient_data.get('TCKimlikNo', '---')}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding: 4px 0;">
                <span style="color: #64748b;">Cinsiyet:</span>
                <span style="font-weight: bold; color: #2563eb;">
                    {'🟦 ERKEK' if str(patient_data.get('Cinsiyet', '')).upper() in ['E', 'ERKEK'] else '🟥 KADIN'}
                </span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                <span style="color: #64748b;">Yaş:</span>
                <span style="font-weight: 600; color: #334155;">{patient_data.get('Yas', '---')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Actions / Note Section
    with st.expander("📝 Klinik Not Ekle", expanded=False):
        note = st.text_area("Notunuzu yazın...", placeholder="Örn: Hasta ağrısının azaldığını belirtti.")
        if st.button("Notu Kaydet", use_container_width=True, type="primary"):
            if note:
                # This would normally call a service
                st.success("Klinik not başarıyla eklendi.")
                # We could trigger an event here via EventBus
            else:
                st.warning("Lütfen bir not giriniz.")
