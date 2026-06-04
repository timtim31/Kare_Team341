policies = (

    # Оператор → Блок нейронного сопряжения (18)
    {"src": "operator",                 "dst": "neural_interface"},

    # 1 (Системный Диспетчер) → 2 (Приоритезатор команд)
    {"src": "system_dispatcher",        "dst": "prioritizer"},

    # 1 (Системный Диспетчер) → 3 (Журнал аудита)
    {"src": "system_dispatcher",        "dst": "audit_log"},

    # 2 (Приоритезатор команд) → 5 (Модуль управления приводами)
    {"src": "prioritizer",              "dst": "drive_control"},

    # 2 (Приоритезатор команд) → 6 (Координатор взаимодействия)
    {"src": "prioritizer",              "dst": "interaction_coordinator"},

    # 3 (Журнал аудита) → 17 (Лаборатория)
    {"src": "audit_log",                "dst": "laboratory"},

    # 3 (Журнал аудита) → 10 (Координатор тактильной связи)
    {"src": "audit_log",                "dst": "tactile_coordinator"},

    # 4 (Модуль сбора сенсорных данных) → 3 (Журнал аудита)
    {"src": "sensor_collector",         "dst": "audit_log"},

    # 4 (Модуль сбора сенсорных данных) → 5 (Модуль управления приводами)
    {"src": "sensor_collector",         "dst": "drive_control"},

    # 4 (Модуль сбора сенсорных данных) → 7 (Анализатор сенсорных данных)
    {"src": "sensor_collector",         "dst": "sensor_analyzer"},

    # 5 (Модуль управления приводами) → 4 (Модуль сбора сенсорных данных)
    {"src": "drive_control",            "dst": "sensor_collector"},

    # 6 (Координатор взаимодействия) → 15 (Чип-ингибитор)
    {"src": "interaction_coordinator",  "dst": "chip_inhibitor"},

    # 7 (Анализатор сенсорных данных) → 9 (Модуль машинного обучения)
    {"src": "sensor_analyzer",          "dst": "ml_module"},

    # 7 (Анализатор сенсорных данных) → 8 (Планировщик траектории)
    {"src": "sensor_analyzer",          "dst": "trajectory_planner"},

    # 8 (Планировщик траектории) → 9 (Модуль машинного обучения)
    {"src": "trajectory_planner",       "dst": "ml_module"},

    # 8 (Планировщик траектории) → 10 (Координатор тактильной связи)
    {"src": "trajectory_planner",       "dst": "tactile_coordinator"},

    # 9 (Модуль машинного обучения) → 8 (Планировщик траектории)
    {"src": "ml_module",                "dst": "trajectory_planner"},

    # 10 (Координатор тактильной связи) → 8 (Планировщик траектории)
    {"src": "tactile_coordinator",      "dst": "trajectory_planner"},

    # 10 (Координатор тактильной связи) → 11 (Внутренний монитор безопасности)
    {"src": "tactile_coordinator",      "dst": "security_monitor"},

    # 11 (Внутренний монитор безопасности) → 15 (Чип-ингибитор)
    {"src": "security_monitor",         "dst": "chip_inhibitor"},

    # 12 (Менеджер обновлений) → 24 (Верификатор)
    {"src": "update_manager",           "dst": "verifier"},

    # 12 (Менеджер обновлений) → 25 (Updater)
    {"src": "update_manager",           "dst": "updater"},

    # 13 (Дешифратор сигнала) → 1 (Системный Диспетчер)
    {"src": "signal_decoder",           "dst": "system_dispatcher"},

    # 14 (Блок сопряжения коммуникации) → 20 (Монитор перегрузки)
    {"src": "comm_block",               "dst": "overload_monitor"},

    # 15 (Чип-ингибитор) → 18 (Блок нейронного сопряжения)
    {"src": "chip_inhibitor",           "dst": "neural_interface"},

    # 16 (Система питания) → 21 (Интерфейс аварийного отключения)
    {"src": "power_system",             "dst": "emergency_interface"},

    # 17 (Лаборатория) → 23 (Сервер)
    {"src": "laboratory",               "dst": "server"},

    # 18 (Блок нейронного сопряжения) → 13 (Дешифратор сигнала)
    {"src": "neural_interface",         "dst": "signal_decoder"},

    # 18 (Блок нейронного сопряжения) → Оператор
    {"src": "neural_interface",         "dst": "operator"},

    # 19 (Драйвер привода) → 20 (Монитор перегрузки)
    {"src": "actuator",                 "dst": "overload_monitor"},

    # 19 (Драйвер привода) → 14 (Блок сопряжения коммуникации)
    {"src": "actuator",                 "dst": "comm_block"},

    # 20 (Монитор перегрузки) → 22 (Система управления датчиками)
    {"src": "overload_monitor",         "dst": "sensor_control"},

    # 20 (Монитор перегрузки) → 19 (Драйвер привода)
    {"src": "overload_monitor",         "dst": "actuator"},

    # 20 (Монитор перегрузки) → 21 (Интерфейс аварийного отключения)
    {"src": "overload_monitor",         "dst": "emergency_interface"},

    # 21 (Интерфейс аварийного отключения) → 16 (Система питания)
    {"src": "emergency_interface",      "dst": "power_system"},

    # 22 (Система управления датчиками) → 4 (Модуль сбора сенсорных данных)
    {"src": "sensor_control",           "dst": "sensor_collector"},

    # 22 (Система управления датчиками) → 20 (Монитор перегрузки)
    {"src": "sensor_control",           "dst": "overload_monitor"},

    # 23 (Сервер) → 12 (Менеджер обновлений)
    {"src": "server",                   "dst": "update_manager"},

    # 24 (Верификатор) → 12 (Менеджер обновлений)
    {"src": "verifier",                 "dst": "update_manager"},

    # 24 (Верификатор) → 26 (Хранилище)
    {"src": "verifier",                 "dst": "storage"},

    # 25 (Updater) → 26 (Хранилище)
    {"src": "updater",                  "dst": "storage"},

    # 26 (Хранилище) → 24 (Верификатор)
    {"src": "storage",                  "dst": "verifier"},

    # Внешний API — единственный разрешённый внешний источник команд
    {"src": "operator_api",             "dst": "system_dispatcher"},
)


def check_operation(id, details) -> bool:
    """ Проверка возможности совершения обращения. """
    src: str = details.get("source")
    dst: str = details.get("deliver_to")

    if not all((src, dst)):
        return False

    print(f"[info] checking polыicies for event {id}, {src}->{dst}")

    return {"src": src, "dst": dst} in policies


# Сценарии вызывающие полную блокировку системы
CRITICAL_SCENARIOS = {"SCENARIO_08", "SCENARIO_12", "SCENARIO_14"}

# Алиас для обратной совместимости
TOPOLOGY_POLICIES = policies