TOPOLOGY = {
    "central_control_system": ["prioritizer", "security_monitor", "inhibitor"],
    "prioritizer":            ["inhibitor"],
    "security_monitor":       ["central_control_system"],
    "ai_module":              ["central_control_system"],
    "inhibitor":              ["drivers"],
    "drivers":                ["overload_monitor"],
    "overload_monitor":       [],
    "neural_interface":       ["central_control_system"],
}

# Описание каждого блока
COMPONENTS = {
    "central_control_system": "Центральная система управления (brain_link.py)",
    "prioritizer":            "Приоритезатор команд (src/prioritizer/queue.py)",
    "security_monitor":       "Монитор безопасности AI (src/ai/security_monitor.py)",
    "ai_module":              "ИИ-модуль (src/ai/client.py)",
    "inhibitor":              "Ингибитор — фильтр политик (src/inhibitor/service.py)",
    "drivers":                "Драйверы манипуляторов (src/drivers/actuator.py)",
    "overload_monitor":       "Монитор перегрузки приводов (src/drivers/overload_monitor.py)",
    "neural_interface":       "Нейроинтерфейс — аварийный канал (brain_link.py)",
}