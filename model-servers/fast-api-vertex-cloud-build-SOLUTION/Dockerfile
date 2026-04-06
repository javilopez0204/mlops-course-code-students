FROM python:3.12

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY app /app
COPY model.pkl /app

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
