import requests

BASE_URL = "http://127.0.0.1:5000"

def run_e2e_tests():
    print("=== ЗАПУСК СКВОЗНОГО ТЕСТИРОВАНИЯ (E2E) ===\n")
    all_passed = True # Флаг успеха

    print("[TEST 1] Сценарий: Проведение эксперимента")
    steps = [{"arm_id": 0, "vector_x": 5, "vector_y": 5, "power": 10, "target_type": "OBJECT"}]
    
    for step in steps:
        response = requests.post(f"{BASE_URL}/commands", json=step)
        if response.status_code == 200:
            print(f"  OK: Команда выполнена.")
        else:
            all_passed = False
            print(f"  ОШИБКА {response.status_code}: {response.json().get('message', 'Текст ошибки не найден')}")

    print("\n[TEST 2] Сценарий: Перемещение")
    all_passed = True
    
    # Имитируем шаг: Щупальца 0 и 1 фиксируются как опоры, 2 и 3 готовятся к движению
    locomotion_steps = [
        {"arm_id": 0, "vector_x": 0, "vector_y": -10, "power": 40, "target_type": "SUPPORT"},
        {"arm_id": 1, "vector_x": 0, "vector_y": -10, "power": 40, "target_type": "SUPPORT"},
        {"arm_id": 2, "vector_x": 10, "vector_y": 20, "power": 30, "target_type": "OBJECT"}, # Перенос лапы
    ]

    for i, step in enumerate(locomotion_steps):
        response = requests.post(f"{BASE_URL}/commands", json=step)
        if response.status_code == 200:
            print(f"  Шаг {i+1} (Арм {step['arm_id']}): Опора/Движение подтверждено.")
        else:
            all_passed = False
            print(f"  Шаг {i+1} (Арм {step['arm_id']}): ЗАБЛОКИРОВАНО. Причина: {response.json().get('message')}")

    # Проверяем итоговый статус системы через API
    print("\n[SYSTEM CHECK] Проверка телеметрии после перемещения:")
    status_resp = requests.get(f"{BASE_URL}/status")
    if status_resp.status_code == 200:
        states = status_resp.json().get('arm_states')
        print(f"  Состояние конечностей: {states}")

    if all_passed:
        print("\nПОЛНЫЙ УСПЕХ: Система работает штатно.")
    else:
        print("\nТЕСТ ПРОВАЛЕН: Ингибитор заблокировал важные функции!")

if __name__ == "__main__":
    run_e2e_tests()