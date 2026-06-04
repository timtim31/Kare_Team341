import sys
import os
sys.path.insert(0, '/app')
os.environ['PYTHONUNBUFFERED'] = '1'

from flask import Flask, jsonify
from src.ai.security_monitor import SecurityMonitor
from src.drivers.overload_monitor import OverloadMonitor
from kafka_client import start_consumer_thread
from datetime import datetime

app = Flask(__name__)
sm = SecurityMonitor()
om = OverloadMonitor()
event_log = []


def log_event(event_type, data):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    entry = {"timestamp": timestamp, "event": event_type, "data": data}
    event_log.append(entry)
    print(f"[{timestamp}] [MONITOR] [{event_type}] {data}", flush=True)
    sys.stdout.flush()


def handle_kafka_message(message):
    """Обрабатывает сообщение из Kafka топика security_events"""
    event_type = message.get("event")
    data = message.get("data", {})

    print(f"[KAFKA] ← Получено: [{event_type}] {data}", flush=True)
    sys.stdout.flush()

    if event_type == "BLOCKED":
        scenario_id = data.get("scenario_id", "UNKNOWN")
        reason = data.get("reason", "")
        sm.record_blocked(scenario_id, reason)
        log_event("BLOCKED", {
            "scenario": scenario_id,
            "reason": reason,
            "arm_id": data.get("arm_id"),
            "sender": data.get("sender"),
            "anomaly_streak": sm.anomaly_streak,
            "under_attack": sm.is_under_attack()
        })
        if sm.is_under_attack():
            log_event("ATTACK_DETECTED", {
                "message": f"🚨 АТАКА: {sm.anomaly_streak} аномалий подряд!"
            })

    elif event_type == "SUCCESS":
        sm.record_success()
        log_event("SUCCESS", {
            "arm_id": data.get("arm_id"),
            "target_type": data.get("target_type"),
            "anomaly_streak_reset": sm.anomaly_streak == 0
        })

    elif event_type == "EMERGENCY_LOCK":
        log_event("EMERGENCY_LOCK", {
            "reason": data.get("reason"),
            "message": "🚨 СИСТЕМА ЗАБЛОКИРОВАНА"
        })

    elif event_type == "RESET":
        sm.reset()
        event_log.clear()
        log_event("RESET", {"message": "Система сброшена"})


# ── REST эндпоинты ──────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'security_monitor'}), 200


@app.route('/security/stats', methods=['GET'])
def stats():
    return jsonify(sm.get_stats()), 200


@app.route('/security/log', methods=['GET'])
def get_log():
    return jsonify({"events": event_log, "total": len(event_log)}), 200


@app.route('/overload/stats', methods=['GET'])
def overload_stats():
    return jsonify(om.get_stats()), 200


if __name__ == '__main__':
    print('[MONITOR] ✅ Монитор безопасности запущен на порту 5001', flush=True)
    print('[MONITOR] Подключение к Kafka...', flush=True)

    thread = start_consumer_thread(handle_kafka_message)
    print(f'[MONITOR] Consumer поток запущен: {thread.is_alive()}', flush=True)

    print('[MONITOR] Эндпоинты:', flush=True)
    print('[MONITOR]   GET /health', flush=True)
    print('[MONITOR]   GET /security/stats', flush=True)
    print('[MONITOR]   GET /security/log', flush=True)

    app.run(host='0.0.0.0', port=5001)