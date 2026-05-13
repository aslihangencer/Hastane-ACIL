import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from core.constants import UIConstants

def render_wait_time_chart(df):
    """
    Renders a compact line chart for wait time trends with Meditech style.
    """
    if df.empty:
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.info(f"🟢 Veritabanı Senkronize / {now}")
        return
        
    fig = px.line(df, x="Hour", y="AvgWait", 
                 title="24 Saat Bekleme Trendi (dk)",
                 labels={"Hour": "Saat", "AvgWait": "dk"},
                 template="plotly_white")
    
    fig.update_traces(line_color='#F472B6', line_width=3, mode='lines+markers', marker=dict(size=8, color='#FB923C'))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=180,
        font=dict(size=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )
    st.plotly_chart(fig, use_container_width=True)

def render_triage_distribution_chart(df):
    """
    Renders a Meditech-style bar chart for Triyaj Dağılımı.
    """
    if df.empty:
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.info(f"🟢 Veritabanı Senkronize / {now}")
        return
        
    fig = px.bar(df, x="OncelikDurumu", y="Sayi", 
                title="Triyaj Dağılımı (Aktif)",
                color="OncelikDurumu",
                color_discrete_map=UIConstants.TRIAGE_COLOR_MAP,
                template="plotly_white")
                
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        height=180,
        font=dict(size=10),
        xaxis=dict(title=None),
        yaxis=dict(title=None)
    )
    st.plotly_chart(fig, use_container_width=True)

def render_shift_intensity_heatmap(df):
    """
    Renders a clinical intensity heatmap (Day vs Hour).
    """
    if df.empty:
        st.caption("🕒 Yoğunluk verisi henüz toplanmadı.")
        return
        
    # Pivot for heatmap
    pivot = df.pivot(index='Gun', columns='Saat', values='VakaSayisi').fillna(0)
    
    fig = px.imshow(pivot, 
                    labels=dict(x="Saat", y="Gün", color="Vaka"),
                    x=pivot.columns,
                    y=pivot.index,
                    color_continuous_scale=[[0, "#FFEB3B"], [0.5, "#FB8C00"], [1, "#D32F2F"]],
                    title="Haftalık Yoğunluk Haritası")
                    
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=30, b=10),
        font=dict(size=10),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

def render_patient_flow_chart(df):
    """
    Renders patient admission trends (Line Chart).
    """
    if df.empty: return
    
    fig = px.line(df, x="Tarih", y="Sayi", 
                 title="Günlük Hasta Geliş Trendi",
                 labels={"Tarih": "Saat", "Sayi": "Vaka"},
                 template="plotly_white")
    
    fig.update_traces(line_color='#818CF8', line_width=3, mode='lines+markers', marker=dict(size=8, color='#A78BFA'))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=180,
        font=dict(size=10),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
    )
    st.plotly_chart(fig, use_container_width=True)

def render_patient_flow_summary(stats):
    """
    Renders a compact operational funnel using Meditech-style badges.
    """
    if not stats:
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.caption(f"🟢 Veritabanı Senkronize / {now}")
        return
        
    cols = st.columns(5)
    flow = [
        {"label": "Kayıt", "val": stats.get('Registered', 0), "icon": "📝", "color": "#f8fafc"},
        {"label": "Bekleyen", "val": stats.get('Waiting', 0), "icon": "⏳", "color": "#fffbeb"},
        {"label": "Müdahale", "val": stats.get('Treatment', 0), "icon": "🩺", "color": "#eff6ff"},
        {"label": "Yatış", "val": stats.get('Admitted', 0), "icon": "🛏️", "color": "#fef2f2"},
        {"label": "Taburcu", "val": stats.get('Discharged', 0), "icon": "✅", "color": "#f0fdf4"}
    ]
    
    for i, f in enumerate(flow):
        with cols[i]:
            st.markdown(f"""
                <div style='text-align:center; padding:8px; background:{f['color']}; border:1px solid #e2e8f0; border-radius:6px;'>
                    <div style='font-size:0.7rem; color:#64748b; font-weight:700; text-transform:uppercase;'>{f['label']}</div>
                    <div style='font-weight:800; font-size:1.1rem; color:#1e293b;'>{int(f['val'])}</div>
                </div>
            """, unsafe_allow_html=True)

def render_system_log(logs_df):
    """
    Renders the recent system logs for the analytics panel.
    """
    st.markdown("<div style='margin-top:15px;'><span style='font-size:0.8rem; font-weight:700; color:#475569;'>📜 SİSTEM LOGU</span></div>", unsafe_allow_html=True)
    if logs_df.empty:
        now = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.caption(f"🟢 Veritabanı Senkronize / {now}")
        return
        
    for idx, row in logs_df.head(5).iterrows():
        action = row.get('IslemTipi', 'İşlem')
        time_str = row.get('IslemZamani', datetime.now()).strftime('%H:%M:%S') if hasattr(row.get('IslemZamani'), 'strftime') else row.get('IslemZamani', '')
        desc = row.get('Aciklama', 'Kayıt güncellendi.')
        table = row.get('TabloAdi', '')
        
        icon = "👨‍⚕️" if table == "ATAMA" else "📝" if action == "INSERT" else "🚪" if table == "CIKIS" else "🛏️" if table == "YATIS" else "🔄"
        
        st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dashed #e2e8f0; font-size:0.85rem;'>
                <div><span>{icon}</span> <span style='color:#1e293b; font-weight:500;'>{action}</span> - <span style='color:#64748b;'>{desc}</span></div>
                <div style='color:#94a3b8; font-size:0.75rem;'>{time_str}</div>
            </div>
        """, unsafe_allow_html=True)

def render_bed_occupancy_donut(df_beds):
    """
    Renders a donut chart for bed occupancy status.
    """
    if df_beds.empty:
        st.caption("🛏️ Yatak verisi bulunamadı.")
        return
        
    counts = df_beds['Durum'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index, 
        values=counts.values, 
        hole=.6,
        marker_colors=['#ef4444' if x == 'Dolu' else '#22c55e' for x in counts.index]
    )])
    
    fig.update_layout(
        title="Yatak Doluluk Oranı",
        height=200,
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=10))
    )
    st.plotly_chart(fig, use_container_width=True)
