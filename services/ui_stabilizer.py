import streamlit as st
import time

class UIStabilizer:
    """
    Hospital-Grade UI Stabilization Engine for Streamlit.
    Prevents DOM race conditions, 'removeChild' errors, and Rerun recursion.
    """
    
    MIN_RERUN_INTERVAL = 1.0 # Seconds
    
    @staticmethod
    def initialize():
        """Initializes the stabilization state."""
        if "last_rerun_time" not in st.session_state:
            st.session_state.last_rerun_time = 0.0
        if "render_lock" not in st.session_state:
            st.session_state.render_lock = False

    @staticmethod
    def safe_rerun():
        """
        Executes a throttled rerun to prevent React DOM race conditions.
        Also clears cache to ensure data freshness after writes.
        """
        st.cache_data.clear()
        current_time = time.time()
        time_since_last = current_time - st.session_state.get('last_rerun_time', 0.0)
        
        if time_since_last < UIStabilizer.MIN_RERUN_INTERVAL:
            return 

        st.session_state.last_rerun_time = current_time
        st.session_state.render_lock = False 
        st.rerun()

    @staticmethod
    def lock_ui():
        """Locks the UI to prevent concurrent state updates during critical renders."""
        st.session_state.render_lock = True

    @staticmethod
    def unlock_ui():
        """Unlocks the UI after a safe operation."""
        st.session_state.render_lock = False

    @staticmethod
    def is_locked():
        """Checks if the UI is currently locked."""
        return st.session_state.get("render_lock", False)

    @staticmethod
    def notify_success(msg):
        """Standardized notification that doesn't crash the DOM."""
        placeholder = st.empty()
        placeholder.success(msg)
        time.sleep(0.5) # Minimal hold for visual feedback
        placeholder.empty()
