import streamlit as st

def inject_premium_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Meditech / Epic Style Global Theme */
        .stApp {
            background: #f8fafc;
            font-family: 'Inter', sans-serif;
            color: #1e293b;
        }

        /* Compact Enterprise Cards */
        .premium-card {
            background: #ffffff;
            border-radius: 6px;
            padding: 16px;
            border: 1px solid #e2e8f0;
            margin-bottom: 12px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        /* Dense Header Style */
        h1, h2, h3, h4 { color: #1e3a5f !important; font-weight: 700 !important; margin-bottom: 8px !important; }
        
        /* Form Inputs - Dense */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
            border-radius: 4px !important;
            border: 1px solid #cbd5e1 !important;
            font-size: 0.85rem !important;
            padding: 4px 8px !important;
            min-height: 32px !important;
        }

        /* Professional Buttons - Meditech Blue */
        .stButton>button {
            border-radius: 4px;
            padding: 4px 12px;
            font-weight: 600;
            font-size: 0.8rem;
            background: #2563eb;
            color: white;
            border: none;
            transition: all 0.1s ease;
        }
        .stButton>button:hover { background: #1d4ed8; border: none; }
        
        /* Dataframes & Tables */
        [data-testid="stDataFrame"] { border: 1px solid #e2e8f0; border-radius: 4px; }
        
        /* Custom Staff Badge */
        .staff-card-mini {
            background: #f1f5f9;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 0.75rem;
            color: #475569;
            margin-bottom: 4px;
            border-left: 3px solid #3b82f6;
        }
        
        /* Operational Badges */
        .status-pill {
            padding: 1px 6px;
            border-radius: 3px;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)
