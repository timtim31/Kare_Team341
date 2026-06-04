import os
import json
import threading
import time
from datetime import datetime

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
SECURITY_TOPIC = "security_events"


def get_producer(retries=10, delay=5):
    """Создаёт Kafka producer с повторными попытками подключения"""
    for attempt in range(1, retries + 1):
        try:
            from kafka import KafkaProducer
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                request_timeout_ms=5000
            )
            print(f"[KAFKA] ✅ Producer подключён к {KAFKA_BROKER}")
            return producer
        except Exception as e:
            print(f"[KAFKA] Попытка {attempt}/{retries} — Producer недоступен: {e}")
            if attempt < retries:
                time.sleep(delay)
    print(f"[KAFKA] ❌ Producer не смог подключиться после {retries} попыток")
    return None


def send_event(producer, event_type, data):
    """Отправляет событие в Kafka топик"""
    if producer is None:
        print(f"[KAFKA] ⚠️  Producer недоступен — событие [{event_type}] не отправлено")
        return False
    try:
        message = {
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "event": event_type,
            "data": data
        }
        producer.send(SECURITY_TOPIC, value=message)
        producer.flush()
        print(f"[KAFKA] → Топик '{SECURITY_TOPIC}': [{event_type}] {data}")
        return True
    except Exception as e:
        print(f"[KAFKA] Ошибка отправки: {e}")
        return False


def start_consumer_thread(handler_func, retries=10, delay=5):
    """Запускает consumer в отдельном потоке с повторными попытками"""
    def consume():
        for attempt in range(1, retries + 1):
            try:
                from kafka import KafkaConsumer
                consumer = KafkaConsumer(
                    SECURITY_TOPIC,
                    bootstrap_servers=KAFKA_BROKER,
                    group_id="security_monitor_group",
                    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                    auto_offset_reset='latest',
                    enable_auto_commit=True
                )
                print(f"[KAFKA] ✅ Consumer подключён к топику '{SECURITY_TOPIC}'")
                for message in consumer:
                    try:
                        handler_func(message.value)
                    except Exception as e:
                        print(f"[KAFKA] Ошибка обработки сообщения: {e}")
                return
            except Exception as e:
                print(f"[KAFKA] Попытка {attempt}/{retries} — Consumer недоступен: {e}")
                if attempt < retries:
                    time.sleep(delay)
        print(f"[KAFKA] ❌ Consumer не смог подключиться после {retries} попыток")

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    return thread