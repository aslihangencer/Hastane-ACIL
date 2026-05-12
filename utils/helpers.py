from datetime import datetime

def format_date_tr(date_val):
    if not date_val:
        return ""
    
    if isinstance(date_val, str):
        try:
            # Handle YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM
            date_val = datetime.strptime(date_val[:16], "%Y-%m-%d %H:%M")
        except:
            return date_val
            
    # Turkish Month Names
    months = {
        1: "Oca", 2: "Şub", 3: "Mar", 4: "Nis", 5: "May", 6: "Haz",
        7: "Tem", 8: "Ağu", 9: "Eyl", 10: "Eki", 11: "Kas", 12: "Ara"
    }
    
    return f"{date_val.day:02d} {months[date_val.month]} {date_val.year} - {date_val.hour:02d}:{date_val.minute:02d}"
