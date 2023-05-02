FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir

RUN chmod +x ./start.sh

CMD ["start.sh"]