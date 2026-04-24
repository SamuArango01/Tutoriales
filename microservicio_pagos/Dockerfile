FROM python:3.11-alpine

WORKDIR /app

RUN pip install --no-cache-dir flask gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
