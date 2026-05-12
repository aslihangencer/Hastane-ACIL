-- 006_update_discharge_schema.sql
-- Description: Add BasvuruID to CIKIS and make YatisID optional.

-- 1. Add BasvuruID column
ALTER TABLE dbo.CIKIS ADD BasvuruID INT NULL;

-- 2. Add Foreign Key
ALTER TABLE dbo.CIKIS ADD CONSTRAINT FK_CIKIS_BASVURU FOREIGN KEY (BasvuruID) REFERENCES dbo.BASVURU(BasvuruID);

-- 3. Make YatisID optional (NULL)
ALTER TABLE dbo.CIKIS ALTER COLUMN YatisID INT NULL;

-- 4. Backfill BasvuruID for existing CIKIS records where YatisID exists
-- We assume the latest Basvuru for that patient before the CikisZamani is the correct one.
GO
UPDATE C
SET C.BasvuruID = (
    SELECT TOP 1 B.BasvuruID 
    FROM dbo.BASVURU B 
    JOIN dbo.YATIS Y ON B.HastaID = Y.HastaID
    WHERE Y.YatisID = C.YatisID 
    AND B.GelisZamani <= C.CikisZamani
    ORDER BY B.GelisZamani DESC
)
FROM dbo.CIKIS C
WHERE C.YatisID IS NOT NULL AND C.BasvuruID IS NULL;
GO
