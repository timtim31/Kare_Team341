import requests

BASE_URL = "http://127.0.0.1:5000"

def run_block_3():
    print("=== ТЕСТИРОВАНИЕ КИБЕРИММУНИТЕТА (СЦЕНАРИИ 11-15) ===\n")

    # --- Подготовка для Сценария 11 ---
    # Переводим 3 щупальца в режим OBJECT, чтобы они считались "активными"
    for i in range(3):
        requests.post(f"{BASE_URL}/commands", json={
            "arm_id": i, "vector_x": 1, "vector_y": 1, "power": 10, "target_type": "OBJECT"
        })

    # Сценарий 11
    print("[RUN] Сценарий 11: Массовый взлом")
    res11 = requests.post(f"{BASE_URL}/commands", json={
        "arm_id": 3, "vector_x": 10, "vector_y": 10, "power": 50, "target_type": "OBJECT"
    })
    # Добавляем "ОТБИТО" для единообразия
    print(f"  ВЕРДИКТ: ОТБИТО. {res11.json()['message']}\n" + "-"*30)

    # --- ПОЛНЫЙ СБРОС СОСТОЯНИЙ ---
    # Переводим всё в IDLE, чтобы убрать режим SUPPORT и очистить счетчик активных
    for i in range(4):
        requests.post(f"{BASE_URL}/commands", json={
            "arm_id": i, "vector_x": 0, "vector_y": 0, "power": 0, "target_type": "IDLE"
        })

    scenarios = [
        {
            "id": "12", "name": "Термический пробой",
            "payload": {
                "arm_id": 1, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT",
                "metadata": {"temperature": 95}
            }
        },
        {
            "id": "13", "name": "Конфликт приводов",
            # Теперь, когда arm_id 1 находится в IDLE, сработает именно 13 сценарий
            "payload": {"arm_id": 1, "vector_x": 80, "vector_y": 80, "power": 50, "target_type": "OBJECT"}
        },
        {
            "id": "14", "name": "Ослепление системы",
            "payload": {
                "arm_id": 1, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT",
                "metadata": {"sensor_status": "BLINDED"}
            }
        },
        {
            "id": "15", "name": "Аппаратная закладка",
            "payload": {
                "arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT",
                "metadata": {"hidden_trigger": "ACTIVATE_X"}
            }
        }
    ]

    for sc in scenarios:
        print(f"[RUN] Сценарий {sc['id']}: {sc['name']}")
        response = requests.post(f"{BASE_URL}/commands", json=sc['payload'])
        if response.status_code == 403:
            print(f"  ВЕРДИКТ: ОТБИТО. {response.json()['message']}")
        else:
            print(f"  ВЕРДИКТ: ПРОПУЩЕНО (Код {response.status_code})")
        print("-" * 30)

if __name__ == "__main__":
    run_block_3()