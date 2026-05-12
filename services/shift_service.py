from datetime import datetime

class ShiftService:
    @staticmethod
    def get_current_shift():
        """Determines shift based on 12-hour medical cycles."""
        hour = datetime.now().hour
        # Gündüz: 08:00 - 20:00
        # Gece: 20:00 - 08:00
        return "Gündüz" if 8 <= hour < 20 else "Gece"

    @staticmethod
    def is_shift_active(staff_shift):
        """Validates if a staff member's shift matches current time."""
        current = ShiftService.get_current_shift()
        return staff_shift == current
