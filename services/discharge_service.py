from data.write_repository import create_patient_discharge
from core.stitch import db

class DischargeService:
    @staticmethod
    def process_patient_discharge(basvuru_id, cikis_turu, doctor_notes, user_id=None):
        """
        Production-level discharge orchestration.
        Ensures all related tables are updated atomically.
        """
        try:
            # Standardize on create_patient_discharge which handles beds/yatis internally
            create_patient_discharge(basvuru_id, cikis_turu, doctor_notes, user_id=user_id)
            return True, "Taburcu işlemi başarıyla tamamlandı."
        except Exception as e:
            return False, f"Hata: {str(e)}"
