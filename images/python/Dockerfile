# labbox/python: Python 3.12 with pip, venv and pytest.
FROM labbox/base:v1
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv python-is-python3 \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --break-system-packages pytest==8.3.3
USER 1000
