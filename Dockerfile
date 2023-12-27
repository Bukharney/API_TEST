FROM python:3.11.3

WORKDIR /usr/src/app

COPY requirement.txt ./

RUN pip install --no-cache-dir -r requirement.txt

COPY . .  

EXPOSE 8000

CMD ["uvicorn", "app.main:app"]
