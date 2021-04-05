FROM python:3.8.3-alpine

WORKDIR /usr/src/tinder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev libjpeg \
    libwebp openjpeg-dev libimagequant-dev

COPY ./requirements.txt .

COPY ./entrypoint.sh .

COPY . .

ENTRYPOINT ["/usr/src/tinder/entrypoint.sh"]
