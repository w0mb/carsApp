FROM python:3.13.4

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["bash", "-c", "alembic upgrade head && python app/main.py"]