import datetime

class EventBus:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance.logs = []
            cls._instance.subscribers = {}
        return cls._instance

    def subscribe(self, event_name, handler):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(handler)

    def emit(self, event_name, data):
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_name,
            "data": data
        }
        self.logs.append(log_entry)
        print(f"[EVENT BUS] {log_entry['timestamp']} | {event_name}")
        
        # Dispatch to handlers if any
        for handler in self.subscribers.get(event_name, []):
            try:
                handler(data)
            except Exception as e:
                print(f"[EVENT ERROR] Error in handler for {event_name}: {e}")

event_bus = EventBus()
