import streamlit as st
import pandas as pd
from services.ui_stabilizer import UIStabilizer

def render_compact_bed_grid(df, interactive=True):
    """
    Renders a minimalist bed grid with fixed 6-column alignment.
    If interactive=False, it shows status dots (non-clickable).
    If interactive=True, it shows clickable buttons with highlighting.
    """
    if df.empty:
        st.info("Yatak verisi bulunamadı.")
        return

    # Modern Pastel Minimalist Palette
    STATUS_COLORS = {
        "Boş": "#10b981",        # Emerald
        "Dolu": "#ef4444",       # Red
        "Temizlikte": "#f59e0b", # Amber
        "Kirli": "#f59e0b"
    }

    rooms = df['OdaNo'].unique()
    
    for room in rooms:
        st.markdown(f"<div style='font-size:0.7rem; font-weight:700; color:#94a3b8; margin-top:10px; text-transform:uppercase;'>ODA {room}</div>", unsafe_allow_html=True)
        room_df = df[df['OdaNo'] == room]
        
        # Stable 6-column grid for consistent vertical alignment
        cols = st.columns(6)
        for idx, (_, bed) in enumerate(room_df.iterrows()):
            color = STATUS_COLORS.get(bed['Durum'], "#cbd5e1")
            
            # Selection Highlight Logic (Professional Null-safe approach)
            sel_bed = st.session_state.get('selected_bed') or {}
            is_selected = sel_bed.get('YatakID') == bed['YatakID']
            bg_color = "#E0F2FE" if is_selected else "#ffffff"
            border_style = "2px solid #3b82f6" if is_selected else "1px solid #f1f5f9"
            
            with cols[idx % 6]:
                if interactive:
                    # Management Mode: Clickable with Highlight
                    btn_key = f"bed_mng_{bed['YatakID']}"
                    if st.button(f"{bed['YatakNo']}", key=btn_key, use_container_width=True):
                        st.session_state.selected_bed = bed.to_dict()
                        UIStabilizer.safe_rerun()
                    
                    st.markdown(f"""
                        <style>
                        div[data-testid='stButton'] button[key='{btn_key}'] {{ 
                            border: {border_style} !important; 
                            background-color: {bg_color} !important; 
                            border-top: 4px solid {color} !important; 
                            font-weight: 700 !important; 
                            font-size: 0.8rem !important; 
                            height: 45px !important; 
                        }}
                        </style>
                    """, unsafe_allow_html=True)
                else:
                    # Dashboard Mode: Perfectly Aligned Status Dots
                    st.markdown(f"""
                        <div style='display:flex; flex-direction:column; align-items:center; justify-content:center; padding:6px; background:#ffffff; border:1px solid #f1f5f9; border-radius:6px; margin-bottom:8px; min-height:45px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);'>
                            <div style='width:10px; height:10px; background:{color}; border-radius:50%; margin-bottom:4px; box-shadow: 0 0 3px {color}88;'></div>
                            <span style='font-size:0.75rem; font-weight:700; color:#475569; font-family:monospace;'>{bed['YatakNo']}</span>
                        </div>
                    """, unsafe_allow_html=True)

def render_smart_bed_board(df):
    """Fallback smart bed board."""
    if df.empty: return
    for _, row in df.iterrows():
        color = "#10b981" if row['Durum'] == "Boş" else "#ef4444" if row['Durum'] == "Dolu" else "#f59e0b"
        st.markdown(f"<div style='padding:5px 10px; border-radius:4px; border-left:3px solid {color}; background:#f8fafc; margin-bottom:4px; font-size:0.8rem;'><b>{row['OdaNo']}-{row['YatakNo']}</b> <span style='float:right; color:{color}; font-weight:700;'>{row['Durum']}</span></div>", unsafe_allow_html=True)
