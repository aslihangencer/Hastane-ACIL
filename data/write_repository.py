from core.stitch import db
from core.events import event_bus
import json
import numpy as np

def log_audit_event(user_id, table_name, action, old_val=None, new_val=None, desc="", hasta_id=None):
    """Enhanced audit logging with patient context."""
    query = """
    INSERT INTO dbo.AUDIT_LOG (KullaniciID, TabloAdi, IslemTipi, EskiDeger, YeniDeger, Aciklama, HastaID)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    db.execute(query, (user_id, table_name, action, 
                       json.dumps(old_val, default=lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x) if old_val else None, 
                       json.dumps(new_val, default=lambda x: int(x) if isinstance(x, (np.int64, np.int32)) else x) if new_val else None, 
                       desc, hasta_id))

def create_patient(ad, soyad, tc_no, cinsiyet, yas, kan_grubu, user_id=None):
    """Registers a brand new patient into the HASTA table."""
    query = """
    INSERT INTO dbo.HASTA (Ad, Soyad, TCKimlikNo, Cinsiyet, Yas, KanGrubu)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    db.execute(query, (ad, soyad, tc_no, cinsiyet, yas, kan_grubu))
    log_audit_event(user_id, "HASTA", "INSERT", new_val={"ad": ad, "soyad": soyad, "tc": tc_no}, desc=f"Yeni hasta kaydı: {ad} {soyad}")

def get_hasta_id_by_tc(tc_no):
    """
    Returns the patient ID for a given TC Identity Number.
    Used for automated admission after registration.
    """
    return db.fetch_scalar("SELECT HastaID FROM dbo.HASTA WHERE TCKimlikNo = ?", (tc_no,))

def create_patient_admission(hasta_id, sikayet, gelis_sekli, oncelik_id, user_id=None):
    """Creates a new admission with 'Bekliyor' status."""
    oncelik_adi = db.fetch_scalar("SELECT SeviyeAdi FROM dbo.ONCELIK_SEVIYESI WHERE SeviyeID = ?", (oncelik_id,))
    
    query = """
    INSERT INTO dbo.BASVURU (HastaID, Sikayet, GelisSekli, OncelikDurumu, Durum, BasvuruTarihi, GelisZamani)
    VALUES (?, ?, ?, ?, 'Bekliyor', GETDATE(), GETDATE())
    """
    db.execute(query, (hasta_id, sikayet, gelis_sekli, oncelik_adi))
    log_audit_event(user_id, "BASVURU", "INSERT", new_val={"hasta": hasta_id, "oncelik": oncelik_adi}, desc="Yeni acil başvuru kaydı.", hasta_id=hasta_id)
    event_bus.emit("NEW_ADMISSION", {"hasta_id": hasta_id})

def update_patient_state(basvuru_id, yeni_durum, user_id=None):
    """Updates patient outcome in MUDAHALE table (Compatible with new schema)."""
    query = "UPDATE dbo.MUDAHALE SET Sonuc = ? WHERE BasvuruID = ?"
    db.execute(query, (yeni_durum, basvuru_id))
    log_audit_event(user_id, "MUDAHALE", "UPDATE", new_val={"sonuc": yeni_durum}, desc=f"Müdahale sonucu güncellendi: {yeni_durum}")

def assign_staff_to_patient(personel_id, basvuru_id, user_id=None):
    """Assigns staff and moves patient to 'Aktif Hasta' state."""
    hasta_id = db.fetch_scalar("SELECT HastaID FROM dbo.BASVURU WHERE BasvuruID = ?", (basvuru_id,))
    
    queries = [
        ("INSERT INTO dbo.PERSONEL_HASTA_ATAMA (PersonelID, BasvuruID, AtamaZamani, Durum) VALUES (?, ?, GETDATE(), 'Aktif')", 
         (personel_id, basvuru_id)),
        ("UPDATE dbo.PERSONEL SET SonIslemZamani = GETDATE() WHERE PersonelID = ?", (personel_id,)),
        ("UPDATE dbo.BASVURU SET Durum = 'Aktif Hasta' WHERE BasvuruID = ?", (basvuru_id,))
    ]
    db.execute_transaction(queries)
    log_audit_event(user_id, "ATAMA", "INSERT", new_val={"personel": personel_id, "basvuru": basvuru_id}, desc="Hasta personele atandı.", hasta_id=hasta_id)

def transfer_patient_to_bed(hasta_id, yatak_id, user_id=None):
    """Atomic bed transfer: Vacate old -> Occupy new -> Log."""
    queries = [
        # Vacate any existing bed for this patient
        ("UPDATE dbo.YATAKLAR SET Durum = 'Boş' WHERE YatakID IN (SELECT YatakID FROM dbo.YATIS WHERE HastaID = ? AND CikisZamani IS NULL)", (hasta_id,)),
        ("UPDATE dbo.YATIS SET CikisZamani = GETDATE() WHERE HastaID = ? AND CikisZamani IS NULL", (hasta_id,)),
        # Occupy new bed
        ("INSERT INTO dbo.YATIS (HastaID, YatakID, GirisZamani, YatisTarihi) VALUES (?, ?, GETDATE(), CAST(GETDATE() AS DATE))", (hasta_id, yatak_id)),
        ("UPDATE dbo.YATAKLAR SET Durum = 'Dolu' WHERE YatakID = ?", (yatak_id,))
    ]
    db.execute_transaction(queries)
    log_audit_event(user_id, "YATAK_TRANSFER", "TRANSFER", desc=f"Hasta {hasta_id} yatak {yatak_id}'ye transfer edildi.", hasta_id=hasta_id)

def record_discharge(basvuru_id, cikis_turu_id, aciklama, yatis_id=None, yatak_id=None, user_id=None):
    """Refined discharge logic with DISCHARGED status."""
    cikis_adi = db.fetch_scalar("SELECT TuruAdi FROM dbo.CIKIS_TURU WHERE TuruID = ?", (cikis_turu_id,))
    hasta_id = db.fetch_scalar("SELECT HastaID FROM dbo.BASVURU WHERE BasvuruID = ?", (basvuru_id,))
    
    queries = [
        ("INSERT INTO dbo.CIKIS (BasvuruID, YatisID, CikisZamani, CikisTuru, CikisTuruID, Aciklama) VALUES (?, ?, GETDATE(), ?, ?, ?)", 
         (basvuru_id, yatis_id, cikis_adi, cikis_turu_id, aciklama)),
        ("UPDATE dbo.PERSONEL_HASTA_ATAMA SET Durum = 'Tamamlandı' WHERE BasvuruID = ?", (basvuru_id,))
    ]
    
    if yatis_id:
        queries.append(("UPDATE dbo.YATIS SET CikisZamani = GETDATE() WHERE YatisID = ?", (yatis_id,)))
    if yatak_id:
        queries.append(("UPDATE dbo.YATAKLAR SET Durum = 'Boş' WHERE YatakID = ?", (yatak_id,)))
        
    db.execute_transaction(queries)
    log_audit_event(user_id, "CIKIS", "INSERT", new_val={"basvuru": basvuru_id, "yatis": yatis_id}, desc=f"Basvuru {basvuru_id} taburcu edildi.", hasta_id=hasta_id)

def update_bed_status_manual(yatak_id, durum, user_id=None):
    db.execute("UPDATE dbo.YATAKLAR SET Durum = ? WHERE YatakID = ?", (durum, yatak_id))
    log_audit_event(user_id, "YATAKLAR", "UPDATE", new_val={"durum": durum}, desc=f"Yatak {yatak_id} durumu el ile güncellendi: {durum}")

def assign_patient_to_bed(hasta_id, yatak_id, user_id=None):
    """Safely assigns a patient to a bed, ensuring atomic state change."""
    queries = [
        ("UPDATE dbo.YATAKLAR SET Durum = 'Dolu' WHERE YatakID = ?", (yatak_id,)),
        ("INSERT INTO dbo.YATIS (HastaID, YatakID, GirisZamani, YatisTarihi) VALUES (?, ?, GETDATE(), CAST(GETDATE() AS DATE))", (hasta_id, yatak_id))
    ]
    db.execute_transaction(queries)
    log_audit_event(user_id, "YATAK_YONETIMI", "ASSIGN", desc=f"Hasta {hasta_id} yatak {yatak_id}'ye atandı.", hasta_id=hasta_id)

def release_bed(yatak_id, user_id=None):
    """Vacates a bed and closes the active admission record."""
    hasta_id = db.fetch_scalar("SELECT TOP 1 HastaID FROM dbo.YATIS WHERE YatakID = ? AND CikisZamani IS NULL ORDER BY GirisZamani DESC", (yatak_id,))
    queries = [
        ("UPDATE dbo.YATAKLAR SET Durum = 'Boş' WHERE YatakID = ?", (yatak_id,)),
        ("UPDATE dbo.YATIS SET CikisZamani = GETDATE() WHERE YatakID = ? AND CikisZamani IS NULL", (yatak_id,))
    ]
    db.execute_transaction(queries)
    log_audit_event(user_id, "YATAK_YONETIMI", "RELEASE", desc=f"Yatak {yatak_id} boşaltıldı.", hasta_id=hasta_id)

def create_staff(ad, soyad, unvan, uzmanlik, vardiya="Gündüz"):
    db.execute("INSERT INTO dbo.PERSONEL (Ad, Soyad, Unvan, UzmanlikAlani, Vardiya, Durum) VALUES (?, ?, ?, ?, ?, 'Aktif')", 
               (ad, soyad, unvan, uzmanlik, vardiya))

def archive_staff(personel_id, user_id=None):
    db.execute("UPDATE dbo.PERSONEL SET Durum = 'Offline' WHERE PersonelID = ?", (personel_id,))
    log_audit_event(user_id, "PERSONEL", "ARCHIVE", desc=f"Personel {personel_id} arşivlendi.")
