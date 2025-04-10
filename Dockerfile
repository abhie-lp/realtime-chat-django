FROM python:3.13-alpine

RUN apk add --no-cache make gcc musl-dev libpq libpq-dev python3-dev
WORKDIR /app
ENV PORT=80
ENV DOCKER_ENV=1
ENV PYTHONUNBUFFERED=1
EXPOSE 80

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["make", "runserver"]
