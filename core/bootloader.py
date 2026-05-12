import streamlit as st
from core.stitch import db

# Crash-Proof Module Loading
try:
    from data.migrations.engine import MigrationEngine
except ImportError:
    # Fallback if module is physically missing but referenced
    class MigrationEngine:
        @staticmethod
        def auto_migrate(): print("[BOOT] MigrationEngine missing - skipping.")

class Bootloader:
    @staticmethod
    def run_safe_boot():
        """Ensures database connectivity and applies self-healing migrations."""
        try:
            # 1. Connectivity Check
            if not db.test_connection():
                return False
                
            # 2. Run Migration Engine (Self-Healing)
            MigrationEngine.auto_migrate()
            
            return True
        except Exception as e:
            st.error(f"Sistem baslatma hatasi: {e}")
            return False

    @staticmethod
    def render_maintenance_ui():
        """Fallback UI for system outages."""
        st.markdown("""
            <div style='background:#fee2e2; padding:40px; border-radius:15px; text-align:center; border:2px solid #ef4444;'>
                <h1 style='color:#b91c1c;'>⚠️ SİSTEM BAKIMDA</h1>
                <p style='color:#7f1d1d;'>Veritabani baglantisi saglanamiyor veya kritik bir hata olustu.</p>
                <p>Lutfen BT birimi ile iletisime gecin. (Hata Kodu: DB_OFFLINE)</p>
            </div>
        """, unsafe_allow_html=True)
