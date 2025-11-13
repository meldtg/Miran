FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Установка зависимостей с явным указанием версий
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir redis==5.0.1 django-redis==5.4.0

COPY . .

RUN useradd -m myuser
ENV PYTHONPATH=/app/backend

RUN mkdir -p /app/static
RUN python backend/manage.py collectstatic --noinput
RUN chown -R myuser:myuser /app/static

USER myuser

EXPOSE 8000

# Запуск приложения
CMD ["gunicorn", "core.wsgi:application", "--config", "gunicorn.conf.py"]
