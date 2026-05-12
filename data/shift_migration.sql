-- Hospital ERP Shift & Availability Migration
-- Purpose: Support real-time staff workload tracking and assignments

-- 1. Extend PERSONEL with Status and Shift Details
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL]') AND name = 'AktifVardiya')
BEGIN
    ALTER TABLE [dbo].[PERSONEL] ADD [AktifVardiya] NVARCHAR(20) DEFAULT 'Gündüz';
    ALTER TABLE [dbo].[PERSONEL] ADD [PersonelDurumu] NVARCHAR(20) DEFAULT 'Müsait'; -- Müsait, Yoğun, Molada, Offline
    ALTER TABLE [dbo].[PERSONEL] ADD [SonIslemZamani] DATETIME NULL;
    PRINT 'Extended PERSONEL with Shift and Status fields';
END

-- 2. Staff-Patient Assignments Table (Workload Tracking)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PERSONEL_HASTA_ATAMA]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[PERSONEL_HASTA_ATAMA] (
        [AtamaID] INT IDENTITY(1,1) PRIMARY KEY,
        [PersonelID] INT NOT NULL,
        [BasvuruID] INT NOT NULL,
        [AtamaZamani] DATETIME DEFAULT GETDATE(),
        [Durum] NVARCHAR(20) DEFAULT 'Aktif', -- Aktif, Tamamlandı
        FOREIGN KEY ([PersonelID]) REFERENCES [dbo].[PERSONEL]([PersonelID]),
        FOREIGN KEY ([BasvuruID]) REFERENCES [dbo].[BASVURU]([BasvuruID])
    );
    PRINT 'Created PERSONEL_HASTA_ATAMA table';
END

-- 3. Ensure YATIS has BedNo consistency if needed
-- (Assuming YatakID is used for FK, but UI prefers BedNo display)
GO
