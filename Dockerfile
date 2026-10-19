FROM python:3.11-slim-bookworm

LABEL org.opencontainers.image.authors="Paola Vera-Licona"
LABEL org.opencontainers.image.title="Cell Reprogramming Review 2026 reproduction materials"

WORKDIR /repo

ENV MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-liberation fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-all.txt ./
RUN pip install --no-cache-dir -r requirements-all.txt

COPY . .

CMD ["/bin/bash"]
