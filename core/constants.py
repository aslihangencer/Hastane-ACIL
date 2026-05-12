import streamlit as st

class UIConstants:
    APP_NAME = "Hastane Acil Servis"
    VERSION = "1.0.0-PRO"
    PRIMARY_COLOR = "#1D2D50"
    SECONDARY_COLOR = "#3b82f6"
    
    # STATUS_MAP: UI-level localization for database states
    STATUS_MAP = {
        "Registered": "Kayıt",
        "TriageWait": "Triyaj Bekliyor",
        "TriageDone": "Triyaj Tamamlandı",
        "DoctorWait": "Doktor Bekliyor",
        "Active": "Müdahale",
        "Admitted": "Yatış",
        "Discharged": "Taburcu"
    }

    # Meditech Style Color Palette (Dark text on pastel BG)
    MEDITECH_COLORS = {
        "Kırmızı": {"text": "#dc2626", "bg": "#fef2f2"},
        "Sarı": {"text": "#FDE725", "bg": "#fffbeb"},
        "Yeşil": {"text": "#059669", "bg": "#f0fdf4"},
        "Mavi": {"text": "#2563eb", "bg": "#eff6ff"},
        "Gri": {"text": "#475569", "bg": "#f8fafc"}
    }
    
    TRIAGE_COLOR_MAP = {
        "Kırmızı": "#dc2626",
        "Sarı": "#FDE725",
        "Yeşil": "#059669",
        "Mavi": "#2563eb"
    }

    # Wait Time Severity Rules
    WAIT_SEVERITY = {
        "NORMAL": 15,
        "YOGUN": 45
    }

    # Professional Turkish Terms
    TERMS = {
        "dashboard": "Anasayfa",
        "queue": "Hasta Kuyruğu",
        "beds": "Yatak Yönetimi",
        "triage": "Triyaj ve Kayıt",
        "discharge": "Çıkış İşlemleri",
        "reports": "Analitik Raporlar",
        "settings": "Sistem Ayarları",
        "critical": "Kritik Vaka",
        "ambulance": "Ambulans",
        "wait_time": "Bekleme Süresi"
    }
    
    CACHE_TTL = 15 # Enterprise frequency
