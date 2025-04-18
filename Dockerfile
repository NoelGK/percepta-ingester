FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# GENERAL DEPENDENCIES
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# PYTHON DEPENDENCIES
WORKDIR /tmp
  
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN pip install --upgrade pip setuptools wheel poetry
RUN poetry config virtualenvs.create false --local
ENV PEP517_BUILD_BACKEND="setuptools.build_meta"
RUN poetry install --only main --no-root

# APP BUILD
WORKDIR /app
COPY ./ /app/
ENV PYTHONPATH="/app/src"
ENV PYTHONDONTWRITEBYTECODE=1
CMD [ "python3", "src/main.py" ]
