
FROM python:3.9-alpine as builder

COPY Pipfile* /tmp/

RUN apk update && \
    apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev

RUN pip install pipenv && \
    cd /tmp && pipenv lock --requirements > requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /var/BasementBot
COPY . .
COPY config.yml basement_bot

FROM python:3.9-alpine
RUN apk add --no-cache \
    libpq
WORKDIR /var/basement_bot
COPY --from=builder /usr/local /usr/local
COPY --from=builder /var/BasementBot/basement_bot .
CMD python3 -u main.py
