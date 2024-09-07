FROM python:3.10.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements2.txt requirements2.txt
RUN pip install --no-cache-dir -r requirements2.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

