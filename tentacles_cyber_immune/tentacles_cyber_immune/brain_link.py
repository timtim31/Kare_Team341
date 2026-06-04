import os
from src.prioritizer.queue import CommandPrioritizer
from src.ai.security_monitor import SecurityMonitor
from kafka_client import get_producer, send_event

MONITOR_URL = os.getenv("MONITOR_URL", "http://localhost:5001")


class CentralControlSystem:
    def __init__(self, inhibitor, drivers):
        self.inhibitor = inhibitor
        self.drivers = drivers
        self.prioritizer = CommandPrioritizer()
        self.security_monitor = SecurityMonitor()
        self.kafka_producer = get_producer()
        print("[CCS] Центральная система управления инициализирована")
        print(f"[CCS] Kafka брокер: {os.getenv('KAFKA_BROKER', 'localhost:9092')}")

    def _publish(self, event_type, data):
        """Публикует событие в Kafka"""
        send_event(self.kafka_producer, event_type, data)

    def submit(self, request, sender="operator_api",
               biometric_token="USER_4102", metadata=None):

        # Шаг 1 — приоритезация
        self.prioritizer.add(request)
        print(f"[CCS] Очередь: {self.prioritizer.peek_all()}")

        # Шаг 2 — извлечь с наивысшим приоритетом
        next_request = self.prioritizer.pop()

        # Шаг 3 — передать в ингибитор
        success, message = self.inhibitor.authorize_and_execute(
            sender=sender,
            request=next_request,
            callback=self.drivers.execute,
            biometric_token=biometric_token,
            metadata=metadata
        )

        # Шаг 4 — публикуем событие в Kafka
        if not success:
            scenario_id = message.split(":")[0] if "SCENARIO_" in message else "UNKNOWN"
            self.security_monitor.record_blocked(scenario_id, message)

            self._publish("BLOCKED", {
                "scenario_id": scenario_id,
                "reason": message,
                "arm_id": next_request.arm_id,
                "sender": sender
            })

            if self.security_monitor.is_under_attack():
                print("[CCS] ⚠️  АТАКА ОБНАРУЖЕНА — экстренная блокировка!")
                self.inhibitor.is_locked = True
                self._publish("EMERGENCY_LOCK", {
                    "reason": "Превышен порог аномалий",
                    "anomaly_streak": self.security_monitor.anomaly_streak
                })
        else:
            self.security_monitor.record_success()
            self._publish("SUCCESS", {
                "arm_id": next_request.arm_id,
                "target_type": next_request.target_type.name,
                "sender": sender
            })

        return success, message

    def get_status(self):
        return {
            "arm_states": self.inhibitor.arm_states,
            "system_locked": self.inhibitor.is_locked,
            "status": "Active" if not self.inhibitor.is_locked else "LOCKED",
            "security": self.security_monitor.get_stats(),
            "queue_size": len(self.prioritizer.queue)
        }

    def emergency_lock(self):
        print("[CCS] 🚨 АВАРИЙНАЯ БЛОКИРОВКА")
        self.inhibitor.is_locked = True
        self.prioritizer.clear()
        self._publish("EMERGENCY_LOCK", {"reason": "Ручная аварийная блокировка"})

    def reset(self):
        self.inhibitor.is_locked = False
        for arm_id in self.inhibitor.arm_states:
            self.inhibitor.arm_states[arm_id] = "IDLE"
        self.prioritizer.clear()
        self.security_monitor.reset()
        self.drivers.reset()
        self._publish("RESET", {"message": "Система сброшена"})
        print("[CCS] Система полностью сброшена")