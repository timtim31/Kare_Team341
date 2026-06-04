import requests
import time
import unittest
from datetime import datetime

BASE_URL = "http://127.0.0.1:5050"


def log(component, message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    icons = {
        "INFO":  "ℹ️ ",
        "OK":    "✅",
        "FAIL":  "❌",
        "BLOCK": "🔒",
        "SEND":  "📤",
        "RECV":  "📥",
        "WAIT":  "⏳",
    }
    icon = icons.get(status, "•")
    print(f"[{timestamp}] {icon}  [{component}] {message}")


class TestCorsетOperation(unittest.TestCase):

    def _wait_for_task(self, task_id, timeout=30):
        """Ожидает завершения задачи и возвращает результат — как у товарищей"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            resp = requests.get(f"{BASE_URL}/task_result/{task_id}")
            if resp.status_code == 404:
                time.sleep(0.5)
                continue
            data = resp.json()
            if data.get("status") == "done":
                return data
            log("СИСТЕМА", f"Ожидание выполнения задачи {task_id}...", "WAIT")
            time.sleep(0.5)
        self.fail(f"Задача {task_id} не завершилась за {timeout} секунд")

    def _send_command(self, cmd):
        """Отправляет команду и возвращает task_id"""
        arm = cmd.get("arm_id")
        target = cmd.get("target_type")
        vx = cmd.get("vector_x")
        vy = cmd.get("vector_y")
        power = cmd.get("power")

        log("ОПЕРАТОР",        f"Команда: Arm#{arm} → {target} вектор({vx},{vy}) мощность={power}%", "SEND")
        log("ДЕШИФРАТОР(13)",  f"Декодирование нейропакета Arm#{arm}", "INFO")
        log("ЦСУ(1)",          f"Получена команда Arm#{arm} → {target}", "INFO")
        log("ЖУРНАЛ(3)",       f"Регистрация события Arm#{arm} → {target}", "INFO")
        log("ПРИОРИТЕЗАТОР(2)", f"Приоритет: {'SUPPORT=1' if target=='SUPPORT' else 'OBJECT=2' if target=='OBJECT' else 'IDLE=3'}", "INFO")
        log("ЧИП-ИНГИБИТОР(15)", f"Передача на проверку политик", "INFO")

        resp = requests.post(f"{BASE_URL}/commands", json=cmd)
        self.assertEqual(resp.status_code, 202, f"Команда не принята: {resp.text}")

        task_id = resp.json()["task_id"]
        log("СЕРВЕР",          f"Задача создана: {task_id}", "INFO")
        return task_id

    def _check_result(self, task_id, expect_blocked=False):
        """Ждёт результат и проверяет его"""
        result = self._wait_for_task(task_id)
        arm_id = result.get("arm_id")

        if result.get("blocked"):
            log("ПОЛИТИКИ",         f"ЗАБЛОКИРОВАНО: {result.get('reason')}", "BLOCK")
            log("ЧИП-ИНГИБИТОР(15)", f"Команда уничтожена, Arm#{arm_id} не активирован", "BLOCK")
            log("МОНИТОР(11)",      f"Аномалия зафиксирована", "FAIL")
            if not expect_blocked:
                self.fail(f"Команда неожиданно заблокирована: {result.get('reason')}")
        else:
            log("ПОЛИТИКИ",    f"Все проверки пройдены ✓", "OK")
            log("ДРАЙВЕР(19)", f"Arm#{arm_id} выполнил команду ✓", "OK")
            log("МОНИТОР(20)", f"Нагрузка Arm#{arm_id} записана", "OK")
            log("ЦСУ(1)",      f"Задача {task_id} завершена успешно ✓", "OK")
            if expect_blocked:
                self.fail(f"Команда должна была быть заблокирована")

        return result

    # ─── ТЕСТ 1: Проведение эксперимента ───────────────────────

    def test_1_experiment(self):
        """Тест 1: Захват объекта манипулятором"""
        print("\n" + "="*60)
        print("  ТЕСТ 1: ПРОВЕДЕНИЕ ЭКСПЕРИМЕНТА — захват объекта")
        print("="*60)

        requests.post(f"{BASE_URL}/debug/reset")
        log("ЦСУ(1)", "Система сброшена в исходное состояние", "OK")

        task_id = self._send_command({
            "arm_id": 0, "vector_x": 5, "vector_y": 5,
            "power": 10, "target_type": "OBJECT"
        })

        self._check_result(task_id, expect_blocked=False)

        status = requests.get(f"{BASE_URL}/status").json()
        log("СИСТЕМА(22)", f"Телеметрия: {status['arm_states']}", "INFO")
        log("СИСТЕМА",     f"Блокировка: {'ДА 🔒' if status['system_locked'] else 'НЕТ ✓'}", "INFO")

    # ─── ТЕСТ 2: Перемещение ───────────────────────────────────

    def test_2_movement(self):
        """Тест 2: Шагающее движение с опорами"""
        print("\n" + "="*60)
        print("  ТЕСТ 2: ПЕРЕМЕЩЕНИЕ — шагающее движение с опорами")
        print("="*60)

        requests.post(f"{BASE_URL}/debug/reset")
        log("ЦСУ(1)", "Система сброшена", "OK")

        steps = [
            {"arm_id": 0, "vector_x": 0,  "vector_y": -10, "power": 40, "target_type": "SUPPORT"},
            {"arm_id": 1, "vector_x": 0,  "vector_y": -10, "power": 40, "target_type": "SUPPORT"},
            {"arm_id": 2, "vector_x": 10, "vector_y": 20,  "power": 30, "target_type": "OBJECT"},
        ]
        names = [
            "Arm#0 устанавливает опору",
            "Arm#1 устанавливает опору",
            "Arm#2 шаговое движение вперёд",
        ]

        for i, (step, name) in enumerate(zip(steps, names), 1):
            print(f"\n  ── Шаг {i}: {name}")
            task_id = self._send_command(step)
            self._check_result(task_id, expect_blocked=False)

            status = requests.get(f"{BASE_URL}/status").json()
            active = sum(1 for s in status['arm_states'].values() if s != "IDLE")
            log("СИСТЕМА(22)", f"Активных манипуляторов: {active}/4", "INFO")

        # Финальная телеметрия
        print()
        status = requests.get(f"{BASE_URL}/status").json()
        for arm, state in status['arm_states'].items():
            icon = "🔵" if state == "SUPPORT" else "🟢" if state == "OBJECT" else "⚪"
            log(f"Arm#{arm}", f"{icon} {state}", "INFO")



if __name__ == "__main__":
    unittest.main(verbosity=2)