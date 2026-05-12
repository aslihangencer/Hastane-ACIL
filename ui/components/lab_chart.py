import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def render_lab_charts(lab_df):
    """Renders charts for lab results with Plotly premium look and Streamlit fallback."""
    st.markdown("### 📊 Laboratuvar Gelişimi")
    
    if lab_df.empty:
        st.info("Kayıtlı laboratuvar sonucu bulunamadı.")
        return

    try:
        import plotly.express as px
        # Modern Plotly Chart (Premium)
        fig = px.line(
            lab_df, 
            x="Tarih", 
            y=["CRP", "WBC"], 
            markers=True,
            title="CRP & WBC Değerleri Zaman Akışı",
            template="plotly_white",
            color_discrete_map={"CRP": "#ef4444", "WBC": "#3b82f6"}
        )
        
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        # Streamlit Native Fallback (Robust)
        st.line_chart(lab_df.set_index("Tarih")[["CRP", "WBC"]])
        st.warning("Not: Plotly kütüphanesi eksik olduğu için temel grafik gösteriliyor.")

    # Detailed Table in Expander
    with st.expander("📝 Detaylı Sonuç Tablosu"):
        st.dataframe(lab_df, use_container_width=True)
