import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def render_empty_state(title="Kayıt Bulunamadı", icon="🩺", action_label=None, action_key=None):
    """
    Standardized empty state component for the whole app.
    """
    st.markdown(f"""
        <div style="text-align: center; padding: 40px 20px; background: white; border-radius: 12px; border: 1px dashed #cbd5e1; margin: 20px 0;">
            <div style="font-size: 3rem; margin-bottom: 15px;">{icon}</div>
            <h3 style="color: #334155; margin-bottom: 10px;">{title}</h3>
            <p style="color: #64748b; font-size: 0.9rem;">Şu anda görüntülenecek herhangi bir veri bulunmuyor.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_key:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button(action_label, key=action_key, use_container_width=True, type="primary"):
                return True
    return False
