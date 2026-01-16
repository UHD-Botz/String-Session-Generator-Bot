FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]