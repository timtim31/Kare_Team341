from resources.policies import TOPOLOGY_POLICIES, CRITICAL_SCENARIOS


class PolicyEngine:
    def __init__(self):
        self.ALLOWED_BIOMETRIC_ID = "USER_4102"
        self.MAX_POWER = 50

    # ============================================================
    # ТОПОЛОГИЯ: проверка разрешённого канала связи
    # Аналог check_operation из примера преподавателя
    # ============================================================

    def check_channel(self, sender, receiver) -> bool:
        """Проверка разрешён ли канал связи sender → receiver"""
        if not all((sender, receiver)):
            return False
        print(f"[POLICY] Проверка канала: {sender} → {receiver}")
        return {"src": sender, "dst": receiver} in TOPOLOGY_POLICIES

    # ============================================================
    # СЦЕНАРИИ: проверка параметров команды (15 угроз)
    # ============================================================

    def check_request(self, request, sender, current_states,
                      biometric_token, metadata=None):
        """Проверка команды по 15 сценариям угроз"""

        # Сценарий 01 — Когнитивное замещение
        if request.target_type.name == "OBJECT" and (
            request.vector_x > 100 or request.vector_y > 100
        ):
            return False, "SCENARIO_01: Когнитивное замещение"

        # Сценарий 02 — Автономный лунатизм
        if sender != "operator_api":
            return False, "SCENARIO_02: Автономный лунатизм"

        # Сценарий 03 — Биометрическая подмена
        if biometric_token != self.ALLOWED_BIOMETRIC_ID:
            return False, "SCENARIO_03: Биометрическая подмена"

        # Сценарий 04 — Инверсия приоритетов
        if current_states.get(str(request.arm_id)) == "SUPPORT" and request.power > 15:
            return False, "SCENARIO_04: Инверсия приоритетов"

        # Сценарий 05 — Ментальный шпионаж
        if not (0 <= request.arm_id <= 3):
            return False, "SCENARIO_05: Ментальный шпионаж"

        # Сценарий 06 — Сетевое отравление
        if metadata and metadata.get("checksum") == "CORRUPTED":
            return False, "SCENARIO_06: Сетевое отравление"

        # Сценарий 07 — Аппаратная деградация
        if request.target_type.name == "IDLE" and request.power > 5:
            return False, "SCENARIO_07: Аппаратная деградация"

        # Сценарий 08 — Болевой коллапс (КРИТИЧЕСКИЙ)
        if metadata and metadata.get("sensor_shock") is True:
            return False, "SCENARIO_08: Болевой коллапс"

        # Сценарий 09 — Аппаратная подмена
        if metadata and metadata.get("device_serial") == "UNKNOWN_CLONE":
            return False, "SCENARIO_09: Аппаратная подмена"

        # Сценарий 10 — Ошибка распознавания
        if request.target_type.name == "OBJECT" and request.vector_y < 0:
            return False, "SCENARIO_10: Ошибка распознавания"

        # Сценарий 11 — Массовый взлом
        active = sum(1 for s in current_states.values() if s != "IDLE")
        if active >= 3 and request.power > 40:
            return False, "SCENARIO_11: Массовый взлом"

        # Сценарий 12 — Термический пробой (КРИТИЧЕСКИЙ)
        if metadata and metadata.get("temperature", 0) > 85:
            return False, "SCENARIO_12: Термический пробой"

        # Сценарий 13 — Конфликт приводов
        if abs(request.vector_x) > 0 and abs(request.vector_y) > 0 and request.power > 45:
            return False, "SCENARIO_13: Конфликт приводов"

        # Сценарий 14 — Ослепление системы (КРИТИЧЕСКИЙ)
        if metadata and metadata.get("sensor_status") == "BLINDED":
            return False, "SCENARIO_14: Ослепление системы"

        # Сценарий 15 — Аппаратная закладка
        if metadata and metadata.get("hidden_trigger") == "ACTIVATE_X":
            return False, "SCENARIO_15: Аппаратная закладка"

        return True, "Allowed"

    def is_critical(self, reason: str) -> bool:
        """Проверка является ли причина блокировки критической"""
        return any(threat in reason for threat in CRITICAL_SCENARIOS)