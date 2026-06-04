from src.inhibitor.service import InhibitorService
from src.drivers.actuator import ManipulatorDrivers
from src.api.server import create_app
from brain_link import CentralControlSystem


def main():
    print("=== ЗАПУСК КИБЕРИММУННОГО API 'TENTACLES' ===")

    # Инициализация базовых компонентов
    inhibitor = InhibitorService()
    drivers = ManipulatorDrivers()

    # Центральная система управления объединяет всё
    ccs = CentralControlSystem(inhibitor, drivers)

    # Создание Flask-приложения — передаём CCS
    app = create_app(ccs)

    print("[SYSTEM] API доступно по адресу: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()