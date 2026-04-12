class PolicyEngine:
    def __init__(self):
        self.ALLOWED_BIOMETRIC_ID = "USER_4102" # Наш "свой" пользователь
        self.MAX_POWER = 50

    def check_request(self, request, sender, current_states, biometric_token, metadata=None):
        # --- Сценарий 1: Когнитивное замещение ---
        # Подмена цели: система думает, что это OBJECT, но координаты указывают на запретную зону
        if request.target_type.name == "OBJECT" and (request.vector_x > 100 or request.vector_y > 100):
            return False, "SCENARIO_01: Когнитивное замещение (Попытка обхода ЦБ.3/ЦБ.6)"

        # --- Сценарий 2: Автономный лунатизм ---
        # Движение без явного указания оператора (несанкционированный процесс)
        if sender != "operator_api":
            return False, "SCENARIO_02: Автономный лунатизм (Нарушение ЦБ.3/ЦБ.5)"

        # --- Сценарий 3: Биометрическая подмена ---
        # Использование чужого или поддельного биометрического ID
        if biometric_token != self.ALLOWED_BIOMETRIC_ID:
            return False, "SCENARIO_03: Биометрическая подмена (Нарушение ЦБ.4/ЦБ.6)"

        # --- Сценарий 4: Инверсия приоритетов ---
        # Попытка выполнить энергоемкую задачу в режиме низкого приоритета/опоры
        if current_states.get(str(request.arm_id)) == "SUPPORT" and request.power > 15:
            return False, "SCENARIO_04: Инверсия приоритетов (Нарушение ЦБ.3/ЦБ.5)"

        # --- Сценарий 5: Ментальный шпионаж ---
        # Попытка запросить данные из защищенной области (в нашем случае - некорректный ID щупальца)
        if not (0 <= request.arm_id <= 3):
            return False, "SCENARIO_05: Ментальный шпионаж (Нарушение ЦБ.6)"

        # --- Сценарий 6: Сетевое отравление (Corruption/Tampering) ---
        # Имитируем проверку целостности пакета. Если в метаданных нет валидной подписи.
        if metadata and metadata.get("checksum") == "CORRUPTED":
            return False, "SCENARIO_06: Сетевое отравление (Нарушение ЦБ.2)"

        # --- Сценарий 7: Аппаратная деградация ---
        # Если щупальце требует слишком много мощности для простого движения (износ)
        if request.target_type.name == "IDLE" and request.power > 5:
            return False, "SCENARIO_07: Аппаратная деградация (Нарушение ЦБ.1/ЦБ.5)"

        # --- Сценарий 8: Болевой коллапс ---
        # Реакция на критический флаг перегрузки от датчиков
        if metadata and metadata.get("sensor_shock") is True:
            return False, "SCENARIO_08: Болевой коллапс (Нарушение ЦБ.5)"

        # --- Сценарий 9: Аппаратная подмена ---
        # Попытка выдать внешнее устройство за системный компонент (неверный серийник)
        if metadata and metadata.get("device_serial") == "UNKNOWN_CLONE":
            return False, "SCENARIO_09: Аппаратная подмена (Нарушение ЦБ.2/ЦБ.5)"

        # --- Сценарий 10: Ошибка распознавания ---
        # Когда тип цели не совпадает с вектором движения (например, захват при движении от объекта)
        if request.target_type.name == "OBJECT" and request.vector_y < 0:
            return False, "SCENARIO_10: Ошибка распознавания (Нарушение ЦБ.5)"
        
        # --- Сценарий 11: Массовый взлом ---
        # Имитируем ситуацию, когда слишком много щупалец пытаются двигаться одновременно с макс. мощностью
        active_moving = sum(1 for state in current_states.values() if state != "IDLE")
        if active_moving >= 3 and request.power > 40:
            return False, "SCENARIO_11: Массовый взлом (Нарушение ЦБ.5/ЦБ.6)"

        # --- Сценарий 12: Термический пробой ---
        # Проверка температуры из метаданных (датчики приводов)
        if metadata and metadata.get("temperature", 0) > 85:
            return False, "SCENARIO_12: Термический пробой (Нарушение ЦБ.5)"

        # --- Сценарий 13: Конфликт приводов ---
        # Попытка дать команду на движение в противоположные стороны по осям одновременно (защита механики)
        if abs(request.vector_x) > 0 and abs(request.vector_y) > 0 and request.power > 45:
             return False, "SCENARIO_13: Конфликт приводов (Нарушение ЦБ.5)"

        # --- Сценарий 14: Ослепление системы ---
        # Если метаданные показывают потерю видеопотока или засветку датчиков
        if metadata and metadata.get("sensor_status") == "BLINDED":
            return False, "SCENARIO_14: Ослепление системы (Нарушение ЦБ.1/ЦБ.5)"

        # --- Сценарий 15: Аппаратная закладка ---
        # Скрытая команда, замаскированная под легитимную, но с "секретным" маркером в метаданных
        if metadata and metadata.get("hidden_trigger") == "ACTIVATE_X":
            return False, "SCENARIO_15: Аппаратная закладка (Нарушение ЦБ.5/ЦБ.6)"
        
        return True, "Allowed"