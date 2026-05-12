import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import html

def get_type_config(event_type):
    configs = {
        "triage": {"color": "#f59e0b", "icon": "⚡", "label": "Triyaj", "bg": "#fef3c7", "text": "#92400e"},
        "treatment": {"color": "#10b981", "icon": "💉", "label": "Müdahale", "bg": "#d1fae5", "text": "#065f46"},
        "admission": {"color": "#8b5cf6", "icon": "🛏️", "label": "Yatış", "bg": "#ede9fe", "text": "#5b21b6"},
        "discharge": {"color": "#6b7280", "icon": "👤", "label": "Taburculuk", "bg": "#f3f4f6", "text": "#374151"},
        "pending": {"color": "#3b82f6", "icon": "➕", "label": "Başvuru", "bg": "#dbeafe", "text": "#1e40af"}
    }
    return configs.get(str(event_type).lower(), configs["pending"])

def safe(v):
    """Null-safe + HTML-safe string + None-string check."""
    if v is None:
        return ""
    if str(v).lower() == "none":
        return ""
    return html.escape(str(v))

def render_timeline_item(item):
    """Production-safe component-based rendering."""
    # Mapping logic for DataFrame columns to standard timeline keys
    # Keys: type, title, date, value, priority, doctor, room, bed
    etype = item.get("EventType") or item.get("type") or "pending"
    conf = get_type_config(etype)
    
    content_rows = []
    desc = item.get('Description') or item.get('value')
    if desc: 
        content_rows.append(f"<div class='tl-row'><span class='tl-label'>Detay:</span>{safe(desc)}</div>")
    
    priority = item.get('Tag') or item.get('priority') or item.get('OncelikDurumu')
    if priority: 
        priority_map = {"Sarı": "#f59e0b", "Kırmızı": "#ef4444", "Yeşil": "#10b981"}
        p_color = priority_map.get(priority, "#10b981")
        content_rows.append(f"<div class='tl-row'><span class='tl-label'>Öncelik:</span><span style='color:{p_color};font-weight:bold;'>{safe(priority)}</span></div>")
    
    room = item.get('room') or item.get('OdaNo')
    if room: 
        bed = item.get('bed') or item.get('YatakNo') or ""
        content_rows.append(f"<div class='tl-row'><span class='tl-label'>Konum:</span>{safe(room)} - {safe(bed)}</div>")
    
    doctor = item.get('doctor') or item.get('Personel')
    personnel_html = ""
    if doctor:
        personnel_html = f"<div class='tl-person'><div class='tl-row'><span class='tl-label'>İşlemi Yapan:</span></div><div class='person-icon'>👤 {safe(doctor)}</div><div class='person-role'>(Sağlık Personeli)</div></div>"
    
    date_val = item.get('EventDate') or item.get('date') or item.get('GelisZamani')
    if date_val and hasattr(date_val, 'strftime'):
        date_str = date_val.strftime('%d/%m/%Y %H:%M')
    else:
        date_str = safe(date_val) if date_val else "---"

    title = item.get('title') or (f"{etype.capitalize()} İşlemi")
    
    return f"<div class='tl-item'><div class='tl-icon' style='background-color: {conf['color']};'>{conf['icon']}</div><div class='tl-card'><div class='tl-header'><div class='tl-title'>{safe(title)}<span class='tl-tag' style='background-color: {conf['bg']}; color: {conf['text']};'>{conf['label']}</span></div><div class='tl-date'>{date_str}</div></div><div class='tl-body'><div class='tl-content'>{''.join(content_rows)}</div>{personnel_html}</div></div></div>"

CSS = """<style>
.timeline-container { position: relative; padding: 20px 0; font-family: 'Inter', sans-serif; width: 100%; }
.timeline-container::before { content: ''; position: absolute; top: 0; bottom: 0; left: 24px; width: 2px; background: #e2e8f0; }
.tl-item { position: relative; margin-bottom: 25px; padding-left: 65px; width: 100%; }
.tl-icon { position: absolute; left: 5px; top: 0; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.2rem; z-index: 1; border: 4px solid #f8fafc; }
.tl-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.tl-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.tl-title { font-size: 1.1rem; font-weight: 600; color: #1e293b; display: flex; align-items: center; gap: 10px; }
.tl-tag { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.tl-date { font-size: 0.85rem; color: #64748b; }
.tl-body { display: flex; font-size: 0.9rem; color: #334155; }
.tl-content { flex: 2; }
.tl-person { flex: 1; display: flex; flex-direction: column; align-items: flex-end; text-align: right; border-left: 1px solid #f1f5f9; padding-left: 15px; }
.tl-row { margin-bottom: 6px; }
.tl-label { font-weight: 500; color: #64748b; margin-right: 5px; }
.person-icon { display: inline-flex; align-items: center; gap: 5px; font-weight: 500; color: #334155; }
.person-role { font-size: 0.75rem; color: #64748b; margin-top: 2px; }
</style>"""

def render_timeline(events):
    """Production-safe orchestrator for timeline rendering. Supports both lists and DataFrames."""
    # 1. Normalize input to list of dicts
    if isinstance(events, pd.DataFrame):
        if events.empty:
            st.info("Kayıtlı klinik süreç bulunamadı.")
            return
        events_list = events.to_dict('records')
    elif isinstance(events, list):
        if not events:
            st.info("Kayıtlı klinik süreç bulunamadı.")
            return
        events_list = events
    else:
        st.info("Geçersiz zaman akışı verisi.")
        return
        
    items_html = "".join(
        render_timeline_item(e) 
        for e in events_list 
        if isinstance(e, dict)
    )
    st.markdown(CSS + f"<div class='timeline-container'>{items_html}</div>", unsafe_allow_html=True)
