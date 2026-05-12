-- Migration: 004_remove_ip_column.sql
-- Goal: Remove legacy IP_Adresi column from AUDIT_LOG

IF EXISTS (SELECT * FROM sys.columns 
           WHERE object_id = OBJECT_ID(N'[dbo].[AUDIT_LOG]') AND name = 'IP_Adresi')
BEGIN
    ALTER TABLE dbo.AUDIT_LOG DROP COLUMN IP_Adresi;
END
GO
