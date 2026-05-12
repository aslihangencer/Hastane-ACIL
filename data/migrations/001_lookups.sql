-- Hospital ERP - Enterprise Lookup Migration
-- Ensuring professional data integrity and normalization

-- 1. Priority Levels (Triyaj Seviyeleri)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ONCELIK_SEVIYESI]') AND type in (N'U'))
BEGIN
    CREATE TABLE dbo.ONCELIK_SEVIYESI (
        SeviyeID INT IDENTITY(1,1) PRIMARY KEY,
        SeviyeAdi NVARCHAR(20) NOT NULL UNIQUE,
        RenkKodu NVARCHAR(7) NOT NULL
    );
    PRINT 'Created ONCELIK_SEVIYESI lookup';
END

-- Seed data safe insert (MERGE)
MERGE dbo.ONCELIK_SEVIYESI AS target
USING (VALUES
    ('Yeşil', '#008000'),
    ('Sarı', '#FFFF00'),
    ('Kırmızı', '#FF0000')
) AS source (SeviyeAdi, RenkKodu)
ON target.SeviyeAdi = source.SeviyeAdi
WHEN NOT MATCHED THEN
    INSERT (SeviyeAdi, RenkKodu)
    VALUES (source.SeviyeAdi, source.RenkKodu);

-- 2. Discharge Types (Çıkış Türleri)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CIKIS_TURU]') AND type in (N'U'))
BEGIN
    CREATE TABLE dbo.CIKIS_TURU (
        TuruID INT IDENTITY(1,1) PRIMARY KEY,
        TuruAdi NVARCHAR(50) NOT NULL UNIQUE
    );
    PRINT 'Created CIKIS_TURU lookup';
END

MERGE dbo.CIKIS_TURU AS target
USING (VALUES
    ('Taburcu'),
    ('Sevk'),
    ('Vefat'),
    ('Tedavi Reddi')
) AS source (TuruAdi)
ON target.TuruAdi = source.TuruAdi
WHEN NOT MATCHED THEN
    INSERT (TuruAdi)
    VALUES (source.TuruAdi);

-- 3. System Integration (Foreign Keys)
-- Safely add OncelikID to BASVURU
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[BASVURU]') AND name = 'OncelikID')
BEGIN
    ALTER TABLE [dbo].[BASVURU] ADD [OncelikID] INT NULL;
    ALTER TABLE [dbo].[BASVURU] ADD CONSTRAINT FK_BASVURU_ONCELIK FOREIGN KEY (OncelikID) REFERENCES ONCELIK_SEVIYESI(SeviyeID);
    PRINT 'Linked BASVURU to ONCELIK_SEVIYESI';
END

-- Safely add CikisTuruID to CIKIS
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[CIKIS]') AND name = 'CikisTuruID')
BEGIN
    ALTER TABLE [dbo].[CIKIS] ADD [CikisTuruID] INT NULL;
    ALTER TABLE [dbo].[CIKIS] ADD CONSTRAINT FK_CIKIS_TURU FOREIGN KEY (CikisTuruID) REFERENCES CIKIS_TURU(TuruID);
    PRINT 'Linked CIKIS to CIKIS_TURU';
END
