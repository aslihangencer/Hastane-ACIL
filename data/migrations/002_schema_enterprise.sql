-- Hospital ERP - Final Enterprise-Grade Migration
-- Production-Safe, Idempotent, and Audit-Ready

-- 1. PERSONEL Table Enhancements (Workload & Shift Support)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'AktifVardiya')
BEGIN
    ALTER TABLE dbo.PERSONEL ADD AktifVardiya NVARCHAR(20) NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'PersonelDurumu')
BEGIN
    ALTER TABLE dbo.PERSONEL ADD PersonelDurumu NVARCHAR(20) CONSTRAINT DF_PERSONEL_DURUM DEFAULT 'Müsait';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'SonIslemZamani')
BEGIN
    ALTER TABLE dbo.PERSONEL ADD SonIslemZamani DATETIME NULL;
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'Rol')
BEGIN
    ALTER TABLE dbo.PERSONEL ADD Rol NVARCHAR(20) NULL;
END

-- 2. BASVURU Table Enhancements (State Machine & Normalization)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[BASVURU]') AND name = 'Durum')
BEGIN
    ALTER TABLE dbo.BASVURU ADD Durum NVARCHAR(20) CONSTRAINT DF_BASVURU_DURUM DEFAULT 'Registered';
END

-- State Machine Enforcement
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE object_id = OBJECT_ID(N'[dbo].[CK_BASVURU_DURUM]'))
BEGIN
    ALTER TABLE dbo.BASVURU ADD CONSTRAINT CK_BASVURU_DURUM CHECK (Durum IN ('Registered','Triaged','Treated','Discharged'));
END

-- 3. YATAKLAR Table Enhancements (Integrity)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'UQ_YATAK_NO' AND object_id = OBJECT_ID('dbo.YATAKLAR'))
BEGIN
    CREATE UNIQUE INDEX UQ_YATAK_NO ON dbo.YATAKLAR(OdaNo, YatakNo);
    PRINT 'Added Unique Index for Bed Identification';
END

-- 4. PERSONEL_HASTA_ATAMA (High Fidelity Workload Model)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL_HASTA_ATAMA]') AND type = 'U')
BEGIN
    CREATE TABLE dbo.PERSONEL_HASTA_ATAMA (
        AtamaID INT IDENTITY(1,1) PRIMARY KEY,
        PersonelID INT NOT NULL,
        BasvuruID INT NOT NULL,
        AtamaYapanPersonelID INT NULL, -- AUDIT
        AtamaZamani DATETIME DEFAULT GETDATE(),
        Durum NVARCHAR(20) DEFAULT 'Aktif',
        AciliyetSeviyesi NVARCHAR(20) NULL,
        CONSTRAINT FK_Atama_Personel FOREIGN KEY (PersonelID) REFERENCES dbo.PERSONEL(PersonelID),
        CONSTRAINT FK_Atama_Basvuru FOREIGN KEY (BasvuruID) REFERENCES dbo.BASVURU(BasvuruID)
    );
    
    -- Duplicate prevention for active assignments
    CREATE UNIQUE INDEX UX_ActiveAssignment 
    ON dbo.PERSONEL_HASTA_ATAMA(PersonelID, BasvuruID) 
    WHERE Durum = 'Aktif';
    
    PRINT 'Created Enterprise Assignment Table';
END

-- 5. Enhanced AUDIT_LOG (Enterprise Standard)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AUDIT_LOG]') AND type = 'U')
BEGIN
    CREATE TABLE dbo.AUDIT_LOG (
        LogID INT IDENTITY(1,1) PRIMARY KEY,
        KullaniciID INT NULL,
        TabloAdi NVARCHAR(50) NOT NULL,
        IslemTipi NVARCHAR(20) NOT NULL,
        EskiDeger NVARCHAR(MAX) NULL,
        YeniDeger NVARCHAR(MAX) NULL,
        HastaID INT NULL,
        IslemTarihi DATETIME DEFAULT GETDATE(),
        IPAdres NVARCHAR(50) NULL,
        Aciklama NVARCHAR(255) NULL
    );
    PRINT 'Created Enhanced Audit Log';
END
ELSE
BEGIN
    -- Update existing audit log if necessary
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[AUDIT_LOG]') AND name = 'HastaID')
    BEGIN
        ALTER TABLE dbo.AUDIT_LOG ADD HastaID INT NULL, IPAdres NVARCHAR(50) NULL;
        PRINT 'Upgraded AUDIT_LOG with Patient Context';
    END
END
