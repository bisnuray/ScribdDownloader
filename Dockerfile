# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]