FROM python:3.12-slim
LABEL authors="pashk"

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /schedule_bot
COPY requirements.txt .
COPY database .
COPY parsers .
RUN mkdir timetables
COPY settings.py .
COPY schedule_getter.py .
COPY tg_bot.py .
COPY weekdays.py .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R 777 ./

RUN python schedule_getter.py
RUN python parsers/parse_timetables.py
CMD ["python", "tg_bot.py"]
