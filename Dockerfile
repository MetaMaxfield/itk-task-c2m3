FROM python:3.12.11-alpine

LABEL maintainer="MetaMaxfield" version="1.0"

WORKDIR /backend/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY pyproject.toml uv.lock /backend/

RUN uv sync --frozen --no-cache

COPY . /backend/

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]