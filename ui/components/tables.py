import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from core.constants import UIConstants
from services.report_service import ReportService

def render_advanced_table(df, title, report_name="Rapor", hide_columns=None):
    """
    Renders a Meditech-style compact table with sticky header and premium badges.
    """
    if df.empty:
        st.info(f"💡 {title} için şu an aktif kayıt bulunmuyor.")
        return

    # Column Filtering
    if hide_columns:
        df = df.drop(columns=[c for c in hide_columns if c in df.columns])

    # Header Row
    c1, c2 = st.columns([5, 1.2])
    with c1: st.markdown(f"**{title.upper()}**", unsafe_allow_html=True)
    with c2:
        user_name = st.session_state.get('user', {}).get('KullaniciAdi', 'Admin')
        csv = ReportService.generate_csv_report(df, report_name, user_name)
        st.download_button("📥 Export", csv, f"{report_name}.csv", "text/csv", use_container_width=True, key=f"dl_{report_name}")

    # CSS for compact table and badges
    st.markdown("""
        <style>
        .stDataFrame td { font-size: 0.85rem !important; padding: 4px 8px !important; }
        .badge { padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.75rem; display: inline-block; }
        </style>
    """, unsafe_allow_html=True)

    # UI Mapping for Status
    if 'Durum' in df.columns:
        df['Durum'] = df['Durum'].apply(lambda x: UIConstants.STATUS_MAP.get(x, x))

    # Render DataFrame with configuration
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "OncelikDurumu": st.column_config.TextColumn("Triyaj", width="small"),
            "WaitTimeDisplay": st.column_config.TextColumn("Bekleme", width="small"),
            "GelisZamani": st.column_config.DatetimeColumn("Giriş", format="HH:mm"),
        }
    )
