-- Hospital ERP Enterprise Migration Script
-- Purpose: Upgrade schema to professional architecture standards

-- 1. HASTA Table: Add Blood Type
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[HASTA]') AND name = 'KanGrubu')
BEGIN
    ALTER TABLE [dbo].[HASTA] ADD [KanGrubu] NVARCHAR(5) NULL;
    PRINT 'Added KanGrubu to HASTA';
END

-- 2. BASVURU Table: Add State Machine Status
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[BASVURU]') AND name = 'Durum')
BEGIN
    ALTER TABLE [dbo].[BASVURU] ADD [Durum] NVARCHAR(20) DEFAULT 'Registered';
    PRINT 'Added Durum (State) to BASVURU';
END

-- 3. PERSONEL Table: Add Role and Detailed Fields
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'Rol')
BEGIN
    ALTER TABLE [dbo].[PERSONEL] ADD [Rol] NVARCHAR(20) NULL;
    ALTER TABLE [dbo].[PERSONEL] ADD [GorevTipi] NVARCHAR(50) NULL;
    PRINT 'Added Rol and GorevTipi to PERSONEL';
END

-- 4. AUDIT_LOG Table: Create professional history system
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AUDIT_LOG]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[AUDIT_LOG] (
        [LogID] INT IDENTITY(1,1) PRIMARY KEY,
        [KullaniciID] INT NULL,
        [TabloAdi] NVARCHAR(50) NOT NULL,
        [IslemTipi] NVARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
        [EskiDeger] NVARCHAR(MAX) NULL,
        [YeniDeger] NVARCHAR(MAX) NULL,
        [IslemTarihi] DATETIME DEFAULT GETDATE(),
        [Aciklama] NVARCHAR(255) NULL
    );
    PRINT 'Created AUDIT_LOG table';
END

-- 5. YATAKLAR Table: Ensure BedNo constraints
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[YATAKLAR]') AND name = 'YatakNo')
BEGIN
    PRINT 'Warning: YatakNo is missing, check original schema.';
END
GO
