from data.write_repository import create_patient
from core.events import event_bus

class PatientService:
    @staticmethod
    def register_new_patient(tc, ad, soyad, yas, cinsiyet, oncelik):
        data = {
            "tc": tc,
            "ad": ad,
            "soyad": soyad,
            "yas": yas,
            "cinsiyet": cinsiyet,
            "oncelik": oncelik
        }
        
        hasta_id = create_patient(data)
        
        # Fire Event
        event_bus.emit("PATIENT_CREATED", {"hasta_id": hasta_id, "tc": tc, "ad": ad})
        
        return hasta_id
