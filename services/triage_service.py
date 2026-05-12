from data.write_repository import create_triage_admission
from core.events import event_bus
from core.constants import UIConstants

class TriageService:
    @staticmethod
    def calculate_score(sikayet):
        sikayet_lower = sikayet.lower()
        total_score = 0
        
        for symptom, weight in UIConstants.TRIAGE_RULES.items():
            if symptom.lower() in sikayet_lower:
                total_score += weight
        
        return total_score

    @staticmethod
    def evaluate_and_admit(hasta_id, sikayet, gelis_sekli_id=1):
        score = TriageService.calculate_score(sikayet)
        
        priority = "Yeşil"
        if score >= 90:
            priority = "Kırmızı"
        elif score >= 50:
            priority = "Sarı"
            
        # Write to DB via CQRS write model
        # Note: Added gelis_sekli_id support based on schema discovery
        create_triage_admission(hasta_id, sikayet, priority, gelis_sekli_id)
        
        # Fire Event
        event_bus.emit("TRIAGE_ASSIGNED", {
            "hasta_id": hasta_id, 
            "priority": priority, 
            "score": score, 
            "symptom": sikayet,
            "flow_state": "TRIAGED"
        })
        
        return priority, score
