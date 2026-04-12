from resources.policies import PolicyEngine

class InhibitorService:
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.arm_states = {"0": "IDLE", "1": "IDLE", "2": "IDLE", "3": "IDLE"}
        self.is_locked = False

    def authorize_and_execute(self, sender, request, callback, biometric_token="UNKNOWN", metadata=None):
        # Теперь передаем биометрический токен в движок правил
        is_allowed, reason = self.policy_engine.check_request(
            request, sender, self.arm_states, biometric_token, metadata
        )

        if not is_allowed:
            # Если это Сценарий 8, 12, 14 блокируем систему полностью
            critical_threats = ["SCENARIO_08", "SCENARIO_12", "SCENARIO_14"]
            if any(threat in reason for threat in critical_threats):
                self.is_locked = True
            return False, reason
        
        # Если система уже заблокирована, не выполняем ничего
        if self.is_locked:
            return False, "SYSTEM_LOCKED: Требуется перезагрузка после коллапса"

        success = callback(request)
        if success:
            self.arm_states[str(request.arm_id)] = request.target_type.name
            return True, "Success"
        
        return False, "Hardware Failure"