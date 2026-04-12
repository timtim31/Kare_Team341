from flask import Flask, request, jsonify
from idl.movement import MovementRequest, TargetType

def create_app(inhibitor, drivers):
    app = Flask(__name__)

    # --- 1. GET: Получение статуса системы ---
    @app.route('/status', methods=['GET'])
    def get_status():
        return jsonify({
            "arm_states": inhibitor.arm_states,
            "system_locked": inhibitor.is_locked,
            "status": "Active" if not inhibitor.is_locked else "LOCKED"
        }), 200

    # --- 2. POST: Отправка команды (Главный вход) ---
# ... (начало файла с импортами без изменений)

    @app.route('/commands', methods=['POST'])
    def send_command():
        data = request.json
        bio_id = data.get('biometric_id', "USER_4102") 
        # Добавляем возможность передать отправителя (по умолчанию наш законный API)
        sender_id = data.get('sender', "operator_api") 
        # Извлекаем метаданные (если они есть)
        meta = data.get('metadata', {})

        try:
            move_req = MovementRequest(
                arm_id=data['arm_id'],
                vector_x=data['vector_x'],
                vector_y=data['vector_y'],
                power=data['power'],
                target_type=TargetType[data['target_type'].upper()]
            )

            success, message = inhibitor.authorize_and_execute(
                sender=sender_id,
                request=move_req, 
                callback=drivers.execute,
                biometric_token=bio_id,
                metadata=meta
            ) 

            if success:
                return jsonify({"status": "executed", "message": message}), 200
            else:
                return jsonify({"status": "REJECTED", "message": message}), 403

        except Exception as e:
            print(f"[SERVER ERROR] Ошибка обработки запроса: {e}")
            return jsonify({"status": "error", "message": str(e)}), 400
        
    # --- 3. PUT: Обновление настроек (например, разблокировка) ---
    @app.route('/settings', methods=['PUT'])
    def update_settings():
        data = request.json
        if 'lock' in data:
            inhibitor.is_locked = data['lock']
            return jsonify({"status": "updated", "lock": inhibitor.is_locked}), 200
        return jsonify({"status": "no changes"}), 400

    # --- 4. DELETE: Экстренная остановка ---
    @app.route('/emergency-stop', methods=['DELETE'])
    def emergency_stop():
        inhibitor.is_locked = True
        return jsonify({"status": "EMERGENCY LOCKDOWN ACTIVATED"}), 200

    # --- 5. OPTIONS: Доступные методы ---
    @app.route('/commands', methods=['OPTIONS'])
    def options_commands():
        return jsonify({"allowed_methods": ["GET", "POST", "OPTIONS", "DELETE"]}), 200

    return app