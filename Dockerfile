FROM python:3.14-rc-slim

WORKDIR /app

COPY src/ ./src/

CMD ["python", "src/main.py"]
