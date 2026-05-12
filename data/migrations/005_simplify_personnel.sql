-- 005_simplify_personnel.sql
-- Description: Drop redundant/empty columns from PERSONEL table after ensuring constraints are removed.

-- 1. Drop Default Constraints
DECLARE @ConstraintName nvarchar(200)

-- AktifVardiya
SELECT @ConstraintName = name FROM sys.default_constraints WHERE parent_object_id = OBJECT_ID('dbo.PERSONEL') AND parent_column_id = COLUMNPROPERTY(OBJECT_ID('dbo.PERSONEL'), 'AktifVardiya', 'ColumnId')
IF @ConstraintName IS NOT NULL EXEC('ALTER TABLE dbo.PERSONEL DROP CONSTRAINT ' + @ConstraintName)

-- PersonelDurumu
SELECT @ConstraintName = name FROM sys.default_constraints WHERE parent_object_id = OBJECT_ID('dbo.PERSONEL') AND parent_column_id = COLUMNPROPERTY(OBJECT_ID('dbo.PERSONEL'), 'PersonelDurumu', 'ColumnId')
IF @ConstraintName IS NOT NULL EXEC('ALTER TABLE dbo.PERSONEL DROP CONSTRAINT ' + @ConstraintName)

-- 2. Drop Columns
ALTER TABLE dbo.PERSONEL DROP COLUMN AktifVardiya;
ALTER TABLE dbo.PERSONEL DROP COLUMN Rol;
ALTER TABLE dbo.PERSONEL DROP COLUMN GorevTipi;
ALTER TABLE dbo.PERSONEL DROP COLUMN PersonelDurumu;

-- 3. Update vw_StaffWorkload to use Unvan and Vardiya and join properly with ATAMA
GO
CREATE OR ALTER VIEW dbo.vw_StaffWorkload AS
SELECT 
    P.PersonelID,
    P.Ad + ' ' + P.Soyad AS Personel,
    P.Unvan AS Rol,
    P.UzmanlikAlani,
    P.Vardiya AS AktifVardiya,
    P.Durum AS PersonelDurumu,
    (SELECT COUNT(*) FROM dbo.PERSONEL_HASTA_ATAMA PHA WHERE PHA.PersonelID = P.PersonelID AND PHA.Durum = 'Aktif') AS ActivePatients,
    P.SonIslemZamani
FROM dbo.PERSONEL P;
GO
