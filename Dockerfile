FROM python:3.12-slim
LABEL authors="pashk"

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /schedule_bot

COPY ./ ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 443

RUN python schedule_getter.py
CMD ["python", "tg_bot.py"]
