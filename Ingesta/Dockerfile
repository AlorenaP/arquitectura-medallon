FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY conexion.py ingesta_inicial.py ingesta_continua.py ./
CMD ["python", "ingesta_inicial.py"]
