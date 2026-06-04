from idl.movement import MovementRequest
from src.drivers.overload_monitor import OverloadMonitor


class ManipulatorDrivers:
    def __init__(self):
        self.overload_monitor = OverloadMonitor()
        print("[DRIVERS] Драйверы манипуляторов инициализированы")
        print("[DRIVERS] Монитор перегрузки активирован")

    def execute(self, request: MovementRequest):
        """
        Выполнить команду на физическом манипуляторе.
        Перед выполнением проверяет монитор перегрузки.
        Возвращает (True, "OK") или (False, причина).
        """
        # Проверка монитора перегрузки
        ok, reason = self.overload_monitor.check(request.arm_id, request.power)
        if not ok:
            print(f"[OVERLOAD_MONITOR] ❌ Заблокировано: {reason}")
            return False, reason

        # Записываем нагрузку в историю
        self.overload_monitor.record(request.arm_id, request.power)

        # Выполняем команду (заглушка — в реальной системе здесь управление железом)
        print(f"[HARDWARE] ✅ Щупальце №{request.arm_id} "
              f"движение в ({request.vector_x}, {request.vector_y}) "
              f"с мощностью {request.power}%")
        return True, "OK"

    def reset(self):
        """Сброс монитора перегрузки"""
        self.overload_monitor.reset()
        print("[DRIVERS] Состояние драйверов сброшено")