import os
import logging
from core.stitch import db

logger = logging.getLogger("MigrationEngine")

class MigrationEngine:
    @staticmethod
    def init_migration_table():
        """Creates the internal tracking table for migrations."""
        query = """
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sys_migrations]') AND type in (N'U'))
        BEGIN
            CREATE TABLE dbo.sys_migrations (
                MigrationID INT IDENTITY(1,1) PRIMARY KEY,
                MigrationName NVARCHAR(255) NOT NULL UNIQUE,
                ExecutedAt DATETIME DEFAULT GETDATE(),
                Status NVARCHAR(20) DEFAULT 'Success'
            );
        END
        """
        db.execute(query)

    @staticmethod
    def is_migrated(name):
        """Checks if a specific migration has already been executed."""
        count = db.fetch_scalar("SELECT COUNT(*) FROM dbo.sys_migrations WHERE MigrationName = ?", (name,))
        return count > 0

    @staticmethod
    def run_script(file_path):
        """Executes a single SQL script safely."""
        name = os.path.basename(file_path)
        if MigrationEngine.is_migrated(name):
            logger.info(f"Skipping {name} (Already migrated)")
            return True

        logger.info(f"Executing migration: {name}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by GO if necessary, or execute as blocks
            blocks = content.split('GO')
            for block in blocks:
                if block.strip():
                    db.execute(block)
            
            # Record success
            db.execute("INSERT INTO dbo.sys_migrations (MigrationName) VALUES (?)", (name,))
            logger.info(f"Migration {name} completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Migration {name} FAILED: {e}")
            return False

    @staticmethod
    def auto_migrate(migrations_dir="data/migrations"):
        """Automatically runs all scripts in the migrations directory."""
        MigrationEngine.init_migration_table()
        
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
            return

        scripts = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        for script in scripts:
            success = MigrationEngine.run_script(os.path.join(migrations_dir, script))
            if not success:
                logger.error("Migration chain interrupted due to failure.")
                break
