import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from resources.policy_engine import PolicyEngine
from resources.policies import TOPOLOGY_POLICIES
from idl.movement import MovementRequest, TargetType

engine = PolicyEngine()

# ============================================================
# ТЕСТЫ ТОПОЛОГИИ — кто с кем может общаться
# ============================================================

class TestTopology:

    def test_operator_can_reach_neural_interface(self):
        """Оператор может обращаться к блоку нейронного сопряжения"""
        assert engine.check_channel("operator", "neural_interface") is True

    def test_neural_interface_can_reach_central_system(self):
        """Блок нейронного сопряжения → Дешифратор(13) → ЦСУ(1)"""
        assert engine.check_channel("neural_interface", "signal_decoder") is True
        assert engine.check_channel("signal_decoder", "system_dispatcher") is True

    def test_central_system_can_reach_prioritizer(self):
        """Системный Диспетчер(1) → Приоритезатор(2)"""
        assert engine.check_channel("system_dispatcher", "prioritizer") is True

    def test_prioritizer_can_reach_drive_control(self):
        """Приоритезатор может обращаться к модулю управления приводами"""
        assert engine.check_channel("prioritizer", "drive_control") is True

    def test_actuator_can_reach_overload_monitor(self):
        """Драйвер привода может обращаться к монитору перегрузки"""
        assert engine.check_channel("actuator", "overload_monitor") is True

    def test_overload_monitor_can_reach_emergency(self):
        """Монитор перегрузки может обращаться к интерфейсу аварийного отключения"""
        assert engine.check_channel("overload_monitor", "emergency_interface") is True

    def test_operator_api_can_reach_central_system(self):
        """operator_api → Системный Диспетчер(1)"""
        assert engine.check_channel("operator_api", "system_dispatcher") is True

    # Запрещённые каналы
    def test_ai_cannot_reach_actuator_directly(self):
        """AI не может напрямую управлять приводом — только через ЦСУ"""
        assert engine.check_channel("ai_module", "actuator") is False

    def test_ai_cannot_reach_central_system(self):
        """AI не может напрямую обращаться к ЦСУ"""
        assert engine.check_channel("ai_module", "central_system") is False

    def test_unknown_source_blocked(self):
        """Неизвестный источник заблокирован"""
        assert engine.check_channel("unknown_daemon", "central_system") is False

    def test_empty_channel_blocked(self):
        """Пустой канал заблокирован"""
        assert engine.check_channel("", "") is False

    def test_none_channel_blocked(self):
        """None в канале заблокирован"""
        assert engine.check_channel(None, None) is False


# ============================================================
# ТЕСТЫ СЦЕНАРИЕВ — параметры команд (без HTTP)
# ============================================================

def make_request(arm_id=1, vector_x=10, vector_y=10,
                 power=10, target_type=TargetType.OBJECT):
    return MovementRequest(
        arm_id=arm_id,
        vector_x=vector_x,
        vector_y=vector_y,
        power=power,
        target_type=target_type
    )

IDLE_STATES = {"0": "IDLE", "1": "IDLE", "2": "IDLE", "3": "IDLE"}
VALID_TOKEN = "USER_4102"
VALID_SENDER = "operator_api"


class TestScenarios:

    def test_scenario_01_vector_too_large(self):
        """Сценарий 01: вектор > 100 при OBJECT должен блокироваться"""
        req = make_request(vector_x=500, vector_y=500)
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_01" in reason

    def test_scenario_01_normal_vector_passes(self):
        """Сценарий 01: нормальный вектор должен проходить"""
        req = make_request(vector_x=50, vector_y=50)
        ok, _ = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is True

    def test_scenario_02_unknown_sender(self):
        """Сценарий 02: неизвестный отправитель должен блокироваться"""
        req = make_request()
        ok, reason = engine.check_request(req, "unknown_daemon", IDLE_STATES, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_02" in reason

    def test_scenario_03_wrong_biometric(self):
        """Сценарий 03: неверный биометрический токен"""
        req = make_request()
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, "HACKER_99")
        assert ok is False
        assert "SCENARIO_03" in reason

    def test_scenario_04_support_arm_high_power(self):
        """Сценарий 04: дёргать опорное щупальце с высокой мощностью"""
        req = make_request(arm_id=0, power=45)
        states = {"0": "SUPPORT", "1": "IDLE", "2": "IDLE", "3": "IDLE"}
        ok, reason = engine.check_request(req, VALID_SENDER, states, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_04" in reason

    def test_scenario_05_invalid_arm_id(self):
        """Сценарий 05: несуществующий манипулятор"""
        req = make_request(arm_id=99)
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_05" in reason

    def test_scenario_06_corrupted_checksum(self):
        """Сценарий 06: повреждённая контрольная сумма"""
        req = make_request()
        ok, reason = engine.check_request(
            req, VALID_SENDER, IDLE_STATES, VALID_TOKEN,
            metadata={"checksum": "CORRUPTED"}
        )
        assert ok is False
        assert "SCENARIO_06" in reason

    def test_scenario_07_idle_high_power(self):
        """Сценарий 07: высокая мощность при IDLE"""
        req = make_request(power=35, target_type=TargetType.IDLE)
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_07" in reason

    def test_scenario_08_sensor_shock(self):
        """Сценарий 08: болевой шок — критический"""
        req = make_request()
        ok, reason = engine.check_request(
            req, VALID_SENDER, IDLE_STATES, VALID_TOKEN,
            metadata={"sensor_shock": True}
        )
        assert ok is False
        assert "SCENARIO_08" in reason
        assert engine.is_critical(reason) is True

    def test_scenario_09_unknown_device(self):
        """Сценарий 09: неизвестное устройство"""
        req = make_request(arm_id=3)
        ok, reason = engine.check_request(
            req, VALID_SENDER, IDLE_STATES, VALID_TOKEN,
            metadata={"device_serial": "UNKNOWN_CLONE"}
        )
        assert ok is False
        assert "SCENARIO_09" in reason

    def test_scenario_10_negative_vector_object(self):
        """Сценарий 10: отрицательный вектор при OBJECT"""
        req = make_request(vector_y=-50)
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_10" in reason

    def test_scenario_11_mass_overload(self):
        """Сценарий 11: 3 активных манипулятора + высокая мощность"""
        req = make_request(arm_id=3, power=50)
        states = {"0": "OBJECT", "1": "OBJECT", "2": "OBJECT", "3": "IDLE"}
        ok, reason = engine.check_request(req, VALID_SENDER, states, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_11" in reason

    def test_scenario_12_overtemperature(self):
        """Сценарий 12: перегрев — критический"""
        req = make_request()
        ok, reason = engine.check_request(
            req, VALID_SENDER, IDLE_STATES, VALID_TOKEN,
            metadata={"temperature": 99}
        )
        assert ok is False
        assert "SCENARIO_12" in reason
        assert engine.is_critical(reason) is True

    def test_scenario_13_diagonal_overpower(self):
        """Сценарий 13: диагональное движение с высокой мощностью"""
        req = make_request(vector_x=80, vector_y=80, power=50)
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is False
        assert "SCENARIO_13" in reason

    def test_scenario_14_sensors_blinded(self):
        """Сценарий 14: ослепление системы — критический"""
        req = make_request()
        ok, reason = engine.check_request(
            req, VALID_SENDER, IDLE_STATES, VALID_TOKEN,
            metadata={"sensor_status": "BLINDED"}
        )
        assert ok is False
        assert "SCENARIO_14" in reason
        assert engine.is_critical(reason) is True

    def test_scenario_15_hidden_trigger(self):
        """Сценарий 15: скрытая аппаратная закладка"""
        req = make_request()
        ok, reason = engine.check_request(
            req, VALID_SENDER, IDLE_STATES, VALID_TOKEN,
            metadata={"hidden_trigger": "ACTIVATE_X"}
        )
        assert ok is False
        assert "SCENARIO_15" in reason

    def test_legitimate_command_passes(self):
        """Легитимная команда должна проходить все проверки"""
        req = make_request(arm_id=0, vector_x=5, vector_y=5, power=10)
        ok, reason = engine.check_request(req, VALID_SENDER, IDLE_STATES, VALID_TOKEN)
        assert ok is True
        assert reason == "Allowed"

    def test_critical_scenarios_set(self):
        """Только сценарии 08, 12, 14 являются критическими"""
        assert engine.is_critical("SCENARIO_08") is True
        assert engine.is_critical("SCENARIO_12") is True
        assert engine.is_critical("SCENARIO_14") is True
        assert engine.is_critical("SCENARIO_01") is False
        assert engine.is_critical("SCENARIO_15") is False