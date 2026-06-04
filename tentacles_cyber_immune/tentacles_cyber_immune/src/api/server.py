from flask import Flask, request, jsonify
from idl.movement import MovementRequest, TargetType
import threading
import time
import uuid

def create_app(ccs):
    app = Flask(__name__)
    print("[SERVER] Flask-приложение создано")

    # Хранилище задач: task_id -> {status, message, arm_id}
    tasks = {}

    def execute_task(task_id, move_req, sender, biometric_token, metadata):
        """Выполняет команду асинхронно с симуляцией времени"""
        tasks[task_id]["status"] = "running"

        # Симуляция времени выполнения в зависимости от мощности и вектора
        distance = (abs(move_req.vector_x) + abs(move_req.vector_y))
        execution_time = max(3.0, distance * move_req.power / 50)
        time.sleep(execution_time)

        success, message = ccs.submit(
            request=move_req,
            sender=sender,
            biometric_token=biometric_token,
            metadata=metadata
        )

        if success:
            tasks[task_id]["status"] = "done"
            tasks[task_id]["message"] = f"Манипулятор #{move_req.arm_id} выполнил команду {move_req.target_type.name}"
        else:
            tasks[task_id]["status"] = "done"
            tasks[task_id]["message"] = f"ЗАБЛОКИРОВАНО: {message}"
            tasks[task_id]["blocked"] = True
            tasks[task_id]["reason"] = message

    @app.route('/status', methods=['GET'])
    def get_status():
        return jsonify(ccs.get_status()), 200

    @app.route('/status/security', methods=['GET'])
    def security_status():
        return jsonify(ccs.security_monitor.get_stats()), 200

    @app.route('/commands', methods=['POST'])
    def send_command():
        data = request.json
        try:
            move_req = MovementRequest(
                arm_id=data['arm_id'],
                vector_x=data['vector_x'],
                vector_y=data['vector_y'],
                power=data['power'],
                target_type=TargetType[data['target_type'].upper()]
            )

            print(f"[SERVER] Получена команда: Arm #{move_req.arm_id} -> {move_req.target_type.name}")

            # Создаём задачу
            task_id = f"arm-{move_req.arm_id}-{str(uuid.uuid4())[:8]}"
            tasks[task_id] = {
                "status": "pending",
                "message": None,
                "arm_id": move_req.arm_id,
                "blocked": False,
                "reason": None
            }

            # Запускаем асинхронно
            thread = threading.Thread(
                target=execute_task,
                args=(
                    task_id,
                    move_req,
                    data.get('sender', 'operator_api'),
                    data.get('biometric_id', 'USER_4102'),
                    data.get('metadata', {})
                )
            )
            thread.daemon = True
            thread.start()

            return jsonify({
                "status": "accepted",
                "task_id": task_id,
                "message": f"Команда принята, задача {task_id} запущена"
            }), 202

        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            return jsonify({"status": "error", "message": str(e)}), 400

    @app.route('/task_result/<task_id>', methods=['GET'])
    def task_result(task_id):
        """Получить результат задачи"""
        if task_id not in tasks:
            return jsonify({"status": "not_found"}), 404

        task = tasks[task_id]
        return jsonify({
            "status":   task["status"],
            "message":  task["message"],
            "arm_id":   task["arm_id"],
            "blocked":  task["blocked"],
            "reason":   task["reason"]
        }), 200

    @app.route('/settings', methods=['PUT'])
    def update_settings():
        data = request.json
        if 'lock' in data:
            ccs.inhibitor.is_locked = data['lock']
            return jsonify({"status": "updated", "lock": ccs.inhibitor.is_locked}), 200
        return jsonify({"status": "no changes"}), 400

    @app.route('/emergency-stop', methods=['DELETE'])
    def emergency_stop():
        ccs.emergency_lock()
        return jsonify({"status": "EMERGENCY LOCKDOWN ACTIVATED"}), 200

    @app.route('/commands', methods=['OPTIONS'])
    def options_commands():
        return jsonify({"allowed_methods": ["GET", "POST", "OPTIONS", "DELETE"]}), 200

    @app.route('/debug/reset', methods=['POST'])
    def debug_reset():
        ccs.reset()
        tasks.clear()
        return jsonify({"status": "reset_ok"}), 200

    print("[SERVER] Маршруты зарегистрированы")
    return app