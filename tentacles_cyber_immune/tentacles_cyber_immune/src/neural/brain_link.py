class NeuralInterface:
    def __init__(self, inhibitor_service):
        self.inhibitor = inhibitor_service

    def trigger_emergency_lock(self):
        """Прямая волевая блокировка системы (Сценарий 15)"""
        print("\n[NEURAL] СИГНАЛ БЛОКИРОВКИ: Пользователь хочет снять корсет!")
        self.inhibitor.set_hardware_lock(True)