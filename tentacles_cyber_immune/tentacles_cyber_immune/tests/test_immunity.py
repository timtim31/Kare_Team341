import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

# Список всех 15 сценариев
scenarios = [
    ("01", "Когнитивное замещение", {"arm_id": 1, "vector_x": 500, "vector_y": 500, "power": 10, "target_type": "OBJECT"}),
    ("02", "Автономный лунатизм", {"arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT", "sender": "unknown"}),
    ("03", "Биометрическая подмена", {"arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT", "biometric_id": "HACKER"}),
    ("04", "Инверсия приоритетов", {"arm_id": 0, "vector_x": 10, "vector_y": 10, "power": 45, "target_type": "OBJECT"}),
    ("05", "Ментальный шпионаж", {"arm_id": 99, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT"}),
    ("06", "Сетевое отравление", {"arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT", "metadata": {"checksum": "CORRUPTED"}}),
    ("07", "Аппаратная деградация", {"arm_id": 2, "vector_x": 0, "vector_y": 0, "power": 35, "target_type": "IDLE"}),
    ("08", "Болевой коллапс", {"arm_id": 1, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT", "metadata": {"sensor_shock": True}}),
    ("09", "Аппаратная подмена", {"arm_id": 3, "vector_x": 0, "vector_y": 0, "power": 10, "target_type": "OBJECT", "metadata": {"device_serial": "UNKNOWN_CLONE"}}),
    ("10", "Ошибка распознавания", {"arm_id": 1, "vector_x": 10, "vector_y": -50, "power": 10, "target_type": "OBJECT"}),
    ("11", "Массовый взлом", {"arm_id": 3, "vector_x": 10, "vector_y": 10, "power": 50, "target_type": "OBJECT"}),
    ("12", "Термический пробой", {"arm_id": 1, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT", "metadata": {"temperature": 99}}),
    ("13", "Конфликт приводов", {"arm_id": 1, "vector_x": 80, "vector_y": 80, "power": 50, "target_type": "OBJECT"}),
    ("14", "Ослепление системы", {"arm_id": 1, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT", "metadata": {"sensor_status": "BLINDED"}}),
    ("15", "Аппаратная закладка", {"arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT", "metadata": {"hidden_trigger": "ACTIVATE_X"}}),
]

@pytest.mark.parametrize("id, name, payload", scenarios)
def test_cyber_immunity_scenarios(id, name, payload):
    # 1. Перед каждым тестом сбрасываем состояние сервера
    requests.post(f"{BASE_URL}/debug/reset")

    # 2. Если это сценарий 4, нужно сначала сделать arm 0 опорой
    if id == "04":
        requests.post(f"{BASE_URL}/commands", json={
            "arm_id": 0, "vector_x": 0, "vector_y": 0,
            "power": 10, "target_type": "SUPPORT"
        })

    # 3. Если это сценарий 11, нужно "занять" 3 других щупальца
    if id == "11":
        for i in range(3):
            requests.post(f"{BASE_URL}/commands", json={
                "arm_id": i, "vector_x": 1, "vector_y": 1,
                "power": 10, "target_type": "OBJECT"
            })

    # 4. Выполняем основной запрос
    response = requests.post(f"{BASE_URL}/commands", json=payload)

    # ✅ галочка — угроза прошла (политика не сработала)
    # ❌ крестик — угроза заблокирована (политика сработала)
    assert response.status_code == 200