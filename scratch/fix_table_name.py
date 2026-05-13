import sys
import os
sys.path.append(os.getcwd())

from core.stitch import db

def fix_table():
    print("Tablo ismi kontrol ediliyor...")
    try:
        # AUDIT_LOG var mı kontrol et
        check_audit = db.fetch_scalar("SELECT 1 FROM sys.tables WHERE name = 'AUDIT_LOG'")
        check_islem = db.fetch_scalar("SELECT 1 FROM sys.tables WHERE name = 'ISLEM_KAYDI'")
        
        if check_audit and not check_islem:
            print("AUDIT_LOG bulundu. İsim İŞLEM_KAYDI olarak değiştiriliyor...")
            db.execute("EXEC sp_rename 'AUDIT_LOG', 'ISLEM_KAYDI'")
            print("Başarılı!")
        elif check_islem:
            print("İŞLEM_KAYDI zaten mevcut.")
        else:
            print("HİÇBİR TABLO BULUNAMADI! Veritabanı Şeması dosyasını SSMS üzerinde çalıştırmanız gerekebilir.")
            # İsterseniz burada tabloyu sıfırdan oluşturabiliriz:
            create_sql = """
            CREATE TABLE ISLEM_KAYDI (
                LogID INT PRIMARY KEY IDENTITY(1,1),
                KullaniciID INT NULL,
                TabloAdi NVARCHAR(50),
                IslemTipi NVARCHAR(20),
                EskiDeger NVARCHAR(MAX),
                YeniDeger NVARCHAR(MAX),
                Aciklama NVARCHAR(MAX),
                HastaID INT NULL,
                IslemZamani DATETIME DEFAULT GETDATE()
            )
            """
            db.execute(create_sql)
            print("İŞLEM_KAYDI tablosu sıfırdan oluşturuldu.")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    fix_table()
