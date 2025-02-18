FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install poetry

RUN poetry install --no-root

# Копируем только зависимости (опционально, для оптимизации)
# COPY pyproject.toml poetry.lock ./
# RUN poetry install --no-root

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:main_app", "--host", "0.0.0.0", "--port", "8000"]