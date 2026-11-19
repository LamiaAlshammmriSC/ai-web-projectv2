FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 FLASK_DEBUG=0
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY frontend ./frontend
WORKDIR /app/backend
EXPOSE 5050
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:5050", "app:app"]
