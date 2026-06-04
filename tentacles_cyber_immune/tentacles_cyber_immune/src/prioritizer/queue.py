from dataclasses import dataclass, field
from idl.movement import MovementRequest, TargetType


# Приоритеты — чем меньше цифра, тем раньше выполняется
PRIORITY_MAP = {
    TargetType.SUPPORT: 1,   # опора — наивысший приоритет (безопасность)
    TargetType.OBJECT:  2,   # захват — стандартный приоритет
    TargetType.IDLE:    3,   # бездействие — низкий приоритет
    TargetType.VOID:    99,  # пустота — фактически заблокировано
}


@dataclass(order=True)
class PrioritizedRequest:
    priority: int
    request: MovementRequest = field(compare=False)


class CommandPrioritizer:
    def __init__(self):
        self.queue = []
        print("[PRIORITIZER] Приоритезатор команд инициализирован")
        print(f"[PRIORITIZER] Приоритеты: SUPPORT=1, OBJECT=2, IDLE=3, VOID=99")

    def add(self, request: MovementRequest):
        """Добавить команду в очередь с автоматическим расчётом приоритета"""
        priority = PRIORITY_MAP.get(request.target_type, 99)
        self.queue.append(PrioritizedRequest(priority=priority, request=request))
        self.queue.sort()  # сортировка по приоритету после каждого добавления
        print(f"[PRIORITIZER] ➕ Добавлена: Arm {request.arm_id} "
              f"тип={request.target_type.name} приоритет={priority}")

    def pop(self):
        """Извлечь команду с наивысшим приоритетом"""
        if self.queue:
            item = self.queue.pop(0)
            print(f"[PRIORITIZER] ▶️  Выдана: Arm {item.request.arm_id} "
                  f"тип={item.request.target_type.name} приоритет={item.priority}")
            return item.request
        return None

    def peek_all(self):
        """Показать содержимое очереди без извлечения"""
        return [
            (i.priority, f"Arm{i.request.arm_id}", i.request.target_type.name)
            for i in self.queue
        ]

    def is_empty(self):
        return len(self.queue) == 0

    def clear(self):
        self.queue = []
        print("[PRIORITIZER] Очередь очищена")