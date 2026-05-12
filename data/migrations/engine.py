import os
from core.stitch import db

class MigrationEngine:
    @staticmethod
    def auto_migrate():
        """Automatically detects and applies missing schema elements."""
        try:
            MigrationEngine._ensure_audit_log()
            print("[MIGRATION] Schema check completed successfully.")
        except Exception as e:
            print(f"[MIGRATION ERROR] {e}")

    @staticmethod
    def _ensure_audit_log():
        """Self-healing logic for the Audit Log table."""
        query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AUDIT_LOG')
        BEGIN
            CREATE TABLE dbo.AUDIT_LOG (
                LogID INT IDENTITY(1,1) PRIMARY KEY,
                KullaniciID INT NULL,
                TabloAdi NVARCHAR(50),
                IslemTipi NVARCHAR(20),
                EskiDeger NVARCHAR(MAX),
                YeniDeger NVARCHAR(MAX),
                IslemZamani DATETIME DEFAULT GETDATE(),
                Aciklama NVARCHAR(255),
                HastaID INT NULL
            )
        END
        """
        db.execute(query)
