import os
from dotenv import load_dotenv

# .env dosyasını yüklüyoruz (varsa)
load_dotenv()

class Config:
    # Öğrenci seviyesinde yerel veritabanı bağlantısı
    # Fallback (varsayılan): (localdb)\mssqllocaldb -> Hocanın bilgisayarı için hazır
    # .env içindeki DB_SERVER değeri varsa onu kullanır -> Sizin bilgisayarınız için hazır
    SERVER = os.getenv('DB_SERVER', r'(localdb)\mssqllocaldb')
    DATABASE = os.getenv('DB_NAME', 'HastaneAcilServis')
    DRIVER = os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}')
    
    CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
    
    # UI Ayarları
    APP_NAME = "Acil Servis ERP"
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
