# Описание связей в системе
# Кому разрешено отправлять запросы
TOPOLOGY = {
    "neural_interface": ["inhibitor", "ai_module"],
    "ai_module": ["inhibitor"],
    "inhibitor": ["drivers"],
    "drivers": [] # Драйверы - конечная точка, они никуда не шлют запросы
}