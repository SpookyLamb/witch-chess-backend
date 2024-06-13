ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "PfyV0HeJupExAN5H9srSFngZ8N6InkJdVtAwfabb9CflitKoY7"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "witch_chess.wsgi"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "witch_chess.asgi:application"]