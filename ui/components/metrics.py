import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def render_kpi_row(metrics):
    """
    Renders an enterprise KPI row with animated metrics and delta changes.
    metrics = [
        {"label": "Toplam Başvuru", "value": 124, "delta": "+12%", "color": "blue"},
        ...
    ]
    """
    cols = st.columns(len(metrics))
    for i, m in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
                <div class="kpi-card {m['color']}">
                    <div class="kpi-label">{m['label']}</div>
                    <div class="kpi-value">{m['value']}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">
                        {m.get('delta', '')} <span style="color:#94a3b8">son 24s</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_system_health(health_data):
    """
    Renders the System Health Monitor for Admin panel.
    """
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>🟢 Sistem Sağlık Monitörü</div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SQL Durumu", "Bağlı", help="SQL Server Connection Status")
    c2.metric("Yanıt Süresi", f"{health_data.get('avg_response', 84)}ms", delta="-12ms")
    c3.metric("Aktif Personel", health_data.get('active_staff', 6))
    c4.metric("Boş Yatak", health_data.get('empty_beds', 14), delta="3")
    
    st.markdown("</div>", unsafe_allow_html=True)
