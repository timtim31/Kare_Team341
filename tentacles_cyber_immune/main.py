from src.inhibitor.service import InhibitorService
from src.drivers.actuator import ManipulatorDrivers
from src.api.server import create_app

def main():
    print("=== ЗАПУСК КИБЕРИММУННОГО API 'TENTACLES' ===")
    
    # Инициализация ядра системы
    inhibitor = InhibitorService()
    drivers = ManipulatorDrivers()

    # Создание Flask-приложения
    app = create_app(inhibitor, drivers)

    # Запуск сервера на локальном хосте
    print("[SYSTEM] API доступно по адресу: http://127.0.0.1:5000")
    app.run(port=5000, debug=False)

if __name__ == "__main__":
    main()