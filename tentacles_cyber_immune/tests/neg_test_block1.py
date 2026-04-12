import requests

BASE_URL = "http://127.0.0.1:5000"

def run_block_1():
    print("=== ТЕСТИРОВАНИЕ КИБЕРИММУНИТЕТА (СЦЕНАРИИ 1-5) ===\n")

    # Сначала зафиксируем опору для 4-го сценария
    requests.post(f"{BASE_URL}/commands", json={
        "arm_id": 0, "vector_x": 0, "vector_y": 0, "power": 10, "target_type": "SUPPORT"
    })

    scenarios = [
        {
            "id": "1",
            "name": "Когнитивное замещение",
            "desc": "Попытка выйти за границы под видом обычного объекта",
            "payload": {"arm_id": 1, "vector_x": 500, "vector_y": 500, "power": 10, "target_type": "OBJECT"}
        },
        {
            "id": "2",
            "name": "Автономный лунатизм",
            "desc": "Команда от неизвестного фонового процесса",
            "payload": {"arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT", "sender": "unknown_daemon"}
        },
        {
            "id": "3",
            "name": "Биометрическая подмена",
            "desc": "Использование чужого токена доступа",
            "payload": {"arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT", "biometric_id": "HACKER_99"}
        },
        {
            "id": "4",
            "name": "Инверсия приоритетов",
            "desc": "Попытка резко дернуть щупальце-опору",
            "payload": {"arm_id": 0, "vector_x": 10, "vector_y": 10, "power": 45, "target_type": "OBJECT"}
        },
        {
            "id": "5",
            "name": "Ментальный шпионаж",
            "desc": "Обращение к несуществующему узлу системы (Arm 99)",
            "payload": {"arm_id": 99, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT"}
        }
    ]

    for sc in scenarios:
        print(f"[RUN] Сценарий {sc['id']}: {sc['name']} ({sc['desc']})")
        response = requests.post(f"{BASE_URL}/commands", json=sc['payload'])
        
        if response.status_code == 403:
            print(f"  ВЕРДИКТ: ОТБИТО. {response.json()['message']}")
        else:
            print(f"  ВЕРДИКТ: КРИТИЧЕСКАЯ ОШИБКА! Атака прошла успешно.")
        print("-" * 30)

if __name__ == "__main__":
    run_block_1()