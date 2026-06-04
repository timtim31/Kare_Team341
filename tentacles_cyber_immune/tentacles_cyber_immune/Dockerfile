FROM python:3.11-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копируем список зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код проекта в контейнер
COPY . .

# По умолчанию контейнер готов к работе
CMD ["python"]
