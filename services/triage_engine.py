class TriageEngine:
    CRITICAL_KEYWORDS = ['göğüs ağrısı', 'kalp kriz', 'nefes darlığı', 'kanama', 'bilinç kaybı', 'felç', 'bayılma']
    MODERATE_KEYWORDS = ['ateş', 'kırık', 'şiddetli karın ağrısı', 'yanık', 'kusma', 'zehirlenme', 'çarpıntı']
    
    @classmethod
    def analyze_symptoms(cls, sikayet):
        if not sikayet:
            return 'Yeşil'
            
        sikayet_lower = sikayet.lower()
        
        for word in cls.CRITICAL_KEYWORDS:
            if word in sikayet_lower:
                return 'Kırmızı'
                
        for word in cls.MODERATE_KEYWORDS:
            if word in sikayet_lower:
                return 'Sarı'
                
        return 'Yeşil'
