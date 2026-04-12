from dataclasses import dataclass
from enum import Enum

class TargetType(Enum):
    SUPPORT = 0   # Опора
    OBJECT = 1    # Предмет
    VOID = 2      # Пустота
    IDLE = 3      # Ожидание

@dataclass(frozen=True)
class MovementRequest:
    arm_id: int
    vector_x: int
    vector_y: int
    power: int
    target_type: TargetType