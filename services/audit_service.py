import streamlit as st
from core.events import event_bus
from data.write_repository import db # Assuming we can use db to write to AUDIT_LOG if needed
import re

class AuditService:
    @staticmethod
    def scrub_sensitive_data(data):
        if not data: return data
        data_str = str(data)
        # Scrub 11-digit TC Numbers
        scrubbed = re.sub(r'\d{7}(\d{4})', r'*******\1', data_str)
        return scrubbed

    @staticmethod
    def log_event(event_name, data):
        scrubbed_data = AuditService.scrub_sensitive_data(data)
        user = st.session_state.get('user', {}).get('KullaniciAdi', 'System')
        
        # 1. Console Log (Scrubbed)
        print(f"[AUDIT] {user} performed {event_name}: {scrubbed_data}")
        
        # 2. Event Bus for UI
        event_bus.emit("AUDIT_LOG", {"user": user, "event": event_name, "data": scrubbed_data})
        
        # 3. Optional: Write to dbo.AUDIT_LOG if table exists
        # try:
        #     db.execute("INSERT INTO dbo.AUDIT_LOG (Kullanici, Islem, Hedef, Tarih) VALUES (?, ?, ?, GETDATE())", 
        #                (user, event_name, scrubbed_data[:255]))
        # except: pass

# Subscriptions
event_bus.subscribe("PATIENT_CREATED", lambda d: AuditService.log_event("HASTA_KAYIT", d))
event_bus.subscribe("TRIAGE_ASSIGNED", lambda d: AuditService.log_event("TRIYAJ_ATAMA", d))
event_bus.subscribe("USER_LOGIN", lambda d: AuditService.log_event("SISTEM_GIRIS", d))
event_bus.subscribe("BED_UPDATE", lambda d: AuditService.log_event("YATAK_GUNCELLEME", d))
event_bus.subscribe("DISCHARGE", lambda d: AuditService.log_event("TABURCU_ISLEMI", d))
