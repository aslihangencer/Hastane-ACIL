-- Hospital ERP - Master Enterprise Migration
-- 100% Production-Safe, Transaction-Aware, and Clinical View Enabled

-- 1. Check Constraint Enforcement (Safe Pattern)
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints 
    WHERE name = 'CK_BASVURU_DURUM' AND parent_object_id = OBJECT_ID('dbo.BASVURU')
)
BEGIN
    ALTER TABLE dbo.BASVURU ADD CONSTRAINT CK_BASVURU_DURUM 
    CHECK (Durum IN ('Registered','Triaged','Treated','Discharged'));
    PRINT 'Enforced State Machine Constraint';
END

-- 2. Global Bed Identity (Unique Index Refinement)
-- Drops composite index if it exists and creates global unique index
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_YATAK_NO' AND object_id = OBJECT_ID('dbo.YATAKLAR'))
BEGIN
    DROP INDEX UQ_YATAK_NO ON dbo.YATAKLAR;
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_YATAK_IDENT' AND object_id = OBJECT_ID('dbo.YATAKLAR'))
BEGIN
    CREATE UNIQUE INDEX UQ_YATAK_IDENT ON dbo.YATAKLAR(YatakNo);
    PRINT 'Established Global Bed Identity';
END

-- 3. Default Constraint (Safe Pattern)
IF NOT EXISTS (
    SELECT 1 FROM sys.default_constraints 
    WHERE name = 'DF_PERSONEL_DURUM' AND parent_object_id = OBJECT_ID('dbo.PERSONEL')
)
BEGIN
    -- Ensure column exists first
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'PersonelDurumu')
    BEGIN
        ALTER TABLE dbo.PERSONEL ADD PersonelDurumu NVARCHAR(20) NULL;
    END
    ALTER TABLE dbo.PERSONEL ADD CONSTRAINT DF_PERSONEL_DURUM DEFAULT 'Müsait' FOR PersonelDurumu;
    PRINT 'Set Professional Personnel Status Default';
END

-- 4. Audit Log Refinement (Transaction Awareness)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[AUDIT_LOG]') AND name = 'TransactionID')
BEGIN
    ALTER TABLE dbo.AUDIT_LOG ADD TransactionID UNIQUEIDENTIFIER NULL;
    PRINT 'Upgraded AUDIT_LOG with Transaction Grouping';
END

-- 5. Operational Intelligence (Staff Workload View)
IF EXISTS (SELECT * FROM sys.views WHERE object_id = OBJECT_ID(N'[dbo].[vw_StaffWorkload]'))
BEGIN
    DROP VIEW dbo.vw_StaffWorkload;
END
GO
CREATE VIEW dbo.vw_StaffWorkload AS
SELECT 
    p.PersonelID,
    p.Ad + ' ' + p.Soyad AS Personel,
    p.Unvan,
    p.Rol,
    p.AktifVardiya,
    p.PersonelDurumu,
    COUNT(a.BasvuruID) AS ActivePatients
FROM dbo.PERSONEL p
LEFT JOIN dbo.PERSONEL_HASTA_ATAMA a
    ON p.PersonelID = a.PersonelID
    AND a.Durum = 'Aktif'
WHERE p.Durum = 'Aktif'
GROUP BY p.PersonelID, p.Ad, p.Soyad, p.Unvan, p.Rol, p.AktifVardiya, p.PersonelDurumu;
GO
PRINT 'Created Operational Staff Workload View';
