class Config:
    SERVER = r'.'
    DATABASE = 'HastaneAcilServis'
    DRIVER = '{ODBC Driver 17 for SQL Server}'
    CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;TrustServerCertificate=yes;"
    
    # UI Ayarları
    APP_NAME = "Acil Servis ERP"
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
