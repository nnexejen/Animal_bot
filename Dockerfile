FROM python:3.9-alpine3.22
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY animal_bot.py /infra/all.env /app/
CMD ["python3", "animal_bot.py"]
