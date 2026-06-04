class OverloadMonitor:
    def __init__(self):
        self.load_history = {}  # arm_id -> список последних значений мощности
        self.MAX_AVG_LOAD = 80  # максимальная средняя нагрузка в %
        self.WINDOW = 5         # окно наблюдения — последние N команд

    def record(self, arm_id, power):
        """Записать факт выполнения команды с данной мощностью"""
        key = str(arm_id)
        if key not in self.load_history:
            self.load_history[key] = []
        self.load_history[key].append(power)
        # Держим только последние WINDOW значений
        self.load_history[key] = self.load_history[key][-self.WINDOW:]

    def check(self, arm_id, power):
        """
        Проверить, не приведёт ли новая команда к перегрузке привода.
        Возвращает (True, "OK") или (False, причина).
        """
        key = str(arm_id)
        history = self.load_history.get(key, [])

        if history:
            avg_load = sum(history) / len(history)
            projected = (avg_load * len(history) + power) / (len(history) + 1)
            if projected > self.MAX_AVG_LOAD:
                return False, (
                    f"OVERLOAD: Arm {arm_id} перегружен — "
                    f"средняя нагрузка {avg_load:.1f}%, "
                    f"новая команда {power}% превысит лимит {self.MAX_AVG_LOAD}%"
                )

        return True, "OK"

    def get_stats(self, arm_id=None):
        """Статистика нагрузки по манипулятору или по всем"""
        if arm_id is not None:
            history = self.load_history.get(str(arm_id), [])
            avg = sum(history) / len(history) if history else 0
            return {"arm_id": arm_id, "avg_load": round(avg, 1), "history": history}

        result = {}
        for key, history in self.load_history.items():
            avg = sum(history) / len(history) if history else 0
            result[key] = {"avg_load": round(avg, 1), "history": history}
        return result

    def reset(self, arm_id=None):
        """Сбросить историю нагрузки"""
        if arm_id is not None:
            self.load_history[str(arm_id)] = []
        else:
            self.load_history = {}
        print("[OVERLOAD_MONITOR] История нагрузки сброшена")