FROM python:3.11.3

WORKDIR /usr/src/app

COPY requirement.txt ./

RUN pip install --no-cache-dir -r requirement.txt

COPY . .  

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]