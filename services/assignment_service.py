from data.write_repository import assign_staff_to_patient as db_assign
from data.read_repository import get_staff_availability

class AssignmentService:
    @staticmethod
    def assign_patient(personel_id, basvuru_id, user_id=None):
        """Executes patient assignment with workload validation."""
        # Check current load
        staff = get_staff_availability()
        if staff.empty:
            return False, "Sistem Hatası: Personel verisi alınamadı."
            
        staff_member = staff[staff['PersonelID'] == personel_id]
        
        if not staff_member.empty:
            load = staff_member.iloc[0]['ActivePatients']
            if load >= 5:
                return False, "Kritik Yoğunluk: Bu personelin hasta limiti (5) dolmuştur."
        
        db_assign(personel_id, basvuru_id, user_id)
        return True, "Atama başarılı."

    @staticmethod
    def get_least_loaded_available_doctor():
        """Identifies the doctor with the lowest active patient count."""
        staff = get_staff_availability("Doktor")
        if staff.empty: return None
        
        # Filter for Müsait/Yoğun (not Offline/Molada)
        available = staff[staff['PersonelDurumu'].isin(['Müsait', 'Yoğun'])]
        if available.empty: return None
        
        # Sort by load and return the best candidate
        recommended = available.sort_values(by='ActivePatients').iloc[0]
        return recommended
