from data.write_repository import record_discharge
from core.events import event_bus

class DischargeService:
    @staticmethod
    def process_patient_discharge(yatis_id, yatak_id, cikis_turu, doctor_notes):
        """
        Production-level discharge orchestration.
        Ensures all related tables are updated atomically.
        """
        try:
            record_discharge(yatis_id, yatak_id, cikis_turu, doctor_notes)
            
            # Additional logic: Clear any active alerts for this patient
            # event_bus.emit("CLEAR_ALERTS", {"yatis_id": yatis_id})
            
            return True, "Taburcu işlemi başarıyla tamamlandı."
        except Exception as e:
            return False, f"Hata: {str(e)}"
