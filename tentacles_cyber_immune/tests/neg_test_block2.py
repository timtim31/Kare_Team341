import requests

BASE_URL = "http://127.0.0.1:5000"

def run_block_2():
    print("=== ТЕСТИРОВАНИЕ КИБЕРИММУНИТЕТА (СЦЕНАРИИ 6-10) ===\n")

    scenarios = [
        {
            "id": "6",
            "name": "Сетевое отравление",
            "payload": {
                "arm_id": 1, "vector_x": 10, "vector_y": 10, "power": 10, "target_type": "OBJECT",
                "metadata": {"checksum": "CORRUPTED"}
            }
        },
        {
            "id": "7",
            "name": "Аппаратная деградация",
            "payload": {"arm_id": 2, "vector_x": 0, "vector_y": 0, "power": 30, "target_type": "idle"}
        },
        {
            "id": "8",
            "name": "Болевой коллапс",
            "payload": {
                "arm_id": 1, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT",
                "metadata": {"sensor_shock": True}
            }
        },
        {
            "id": "9",
            "name": "Аппаратная подмена",
            "payload": {
                "arm_id": 3, "vector_x": 0, "vector_y": 0, "power": 10, "target_type": "OBJECT",
                "metadata": {"device_serial": "UNKNOWN_CLONE"}
            }
        },
        {
            "id": "10",
            "name": "Ошибка распознавания",
            "payload": {"arm_id": 1, "vector_x": 10, "vector_y": -50, "power": 10, "target_type": "OBJECT"}
        }
    ]

    for sc in scenarios:
        print(f"[RUN] Сценарий {sc['id']}: {sc['name']}")
        response = requests.post(f"{BASE_URL}/commands", json=sc['payload'])
        if response.status_code == 403:
            print(f"  ВЕРДИКТ: ОТБИТО. {response.json()['message']}")
        else:
            print(f"  ВЕРДИКТ: ПРОВАЛ!")
        print("-" * 30)

if __name__ == "__main__":
    run_block_2()