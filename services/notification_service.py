import streamlit as st
from datetime import datetime

class NotificationService:
    @staticmethod
    def init_notifications():
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []

    @staticmethod
    def push_notification(message, type="info"):
        NotificationService.init_notifications()
        st.session_state.notifications.append({
            "id": len(st.session_state.notifications) + 1,
            "message": message,
            "type": type,
            "time": datetime.now().strftime("%H:%M"),
            "read": False
        })

    @staticmethod
    def get_unread_count():
        NotificationService.init_notifications()
        return len([n for n in st.session_state.notifications if not n['read']])

    @staticmethod
    def mark_all_as_read():
        for n in st.session_state.notifications:
            n['read'] = True

    @staticmethod
    def render_notification_hub():
        with st.expander(f"🔔 Bildirimler ({NotificationService.get_unread_count()})", expanded=False):
            if not st.session_state.notifications:
                st.write("Yeni bildirim yok.")
            else:
                for n in reversed(st.session_state.notifications[-5:]):
                    color = "red" if n['type'] == "error" else "orange" if n['type'] == "warning" else "blue"
                    st.markdown(f"""
                        <div style='padding:8px; border-left: 3px solid {color}; margin-bottom:5px; background:#f9fafb; border-radius:4px;'>
                            <div style='font-size:0.8rem; font-weight:600;'>{n['message']}</div>
                            <div style='font-size:0.7rem; color:gray;'>{n['time']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                if st.button("Hepsini Okundu İşaretle", key="mark_read", use_container_width=True):
                    NotificationService.mark_all_as_read()
                    st.rerun()
