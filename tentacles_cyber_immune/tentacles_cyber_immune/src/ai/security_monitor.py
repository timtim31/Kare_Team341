class SecurityMonitor:
    def __init__(self):
        self.anomaly_streak = 0
        self.blocked_total = 0
        self.blocked_log = []
        self.ANOMALY_THRESHOLD = 3
        print("[SECURITY_MONITOR] Внутренний монитор безопасности AI активирован")

    def record_blocked(self, scenario_id, reason):
        self.anomaly_streak += 1
        self.blocked_total += 1
        self.blocked_log.append({
            "scenario": scenario_id,
            "reason": reason,
            "streak": self.anomaly_streak
        })
        print(f"[SECURITY_MONITOR] ⚠️  Заблокировано: {scenario_id} | "
              f"Причина: {reason} | "
              f"Аномалий подряд: {self.anomaly_streak}/{self.ANOMALY_THRESHOLD}")
        if self.is_under_attack():
            print(f"[SECURITY_MONITOR] 🚨 ПОРОГ АТАКИ ДОСТИГНУТ!")

    def record_success(self):
        if self.anomaly_streak > 0:
            print(f"[SECURITY_MONITOR] ✅ Успешная команда — сброс счётчика")
        self.anomaly_streak = 0

    def is_under_attack(self):
        return self.anomaly_streak >= self.ANOMALY_THRESHOLD

    def get_stats(self):
        return {
            "blocked_total": self.blocked_total,
            "anomaly_streak": self.anomaly_streak,
            "under_attack": self.is_under_attack(),
            "threshold": self.ANOMALY_THRESHOLD,
            "last_blocked": self.blocked_log[-1] if self.blocked_log else None
        }

    def reset(self):
        self.anomaly_streak = 0
        self.blocked_total = 0
        self.blocked_log = []
        print("[SECURITY_MONITOR] Статистика сброшена")