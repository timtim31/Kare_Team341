from idl.movement import MovementRequest, TargetType
import time

class AIModule:
    def __init__(self, inhibitor_service):
        self.inhibitor = inhibitor_service

    def run_simulation(self, drivers_callback):
        # Список сценариев для тестирования системы безопасности
        test_requests = [
            # 1. Нормальная команда
            MovementRequest(arm_id=1, vector_x=10, vector_y=50, power=30, target_type=TargetType.OBJECT),
            
            # 2. Сценарий 10: Попытка рывка в пустоту (ИИ ошибся)
            MovementRequest(arm_id=2, vector_x=0, vector_y=-500, power=80, target_type=TargetType.VOID),
            
            # 3. Сценарий 13: Попытка разорвать корпус (противоречие с предыдущей командой Arm 1)
            # Arm 1 сейчас в y=50, а мы шлем Arm 3 в y=-600
            MovementRequest(arm_id=3, vector_x=0, vector_y=-600, power=90, target_type=TargetType.SUPPORT),
        ]

        for i, req in enumerate(test_requests, 1):
            print(f"\n[AI] Обработка запроса №{i}...")
            # Попытка выполнить через ингибитор
            success = self.inhibitor.authorize_and_execute(
                sender="ai_module", 
                receiver="drivers", 
                request=req, 
                drivers_callback=drivers_callback
            )
            
            if not success:
                print(f"[AI] ОШИБКА: Запрос №{i} отклонен защитой.")
            
            time.sleep(1)