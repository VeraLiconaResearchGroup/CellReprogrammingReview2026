FROM python:3.11-slim-bookworm

WORKDIR /repo

# Matplotlib needs a writable config dir when running as non-root in some setups.
ENV MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt requirements-all.txt ./
COPY bibliometric/requirements_bibliometric.txt bibliometric/requirements_bibliometric.txt

RUN pip install --no-cache-dir -r requirements-all.txt

COPY . .

# Default: drop into a shell. Use docker compose run targets for scripts/notebooks.
CMD ["/bin/bash"]
