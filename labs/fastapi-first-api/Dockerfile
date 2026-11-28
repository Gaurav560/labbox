# labbox/fastapi-first-api:v2 (28 November 2026): Python 3.12 with FastAPI 0.165.0 and everything the course uses,
# installed at build time so chapters and checks work offline. warm/requirements.txt pins every package.
# v1 (FastAPI 0.115.6, one chapter) stays for the live site until it is deployed.
FROM labbox/python:v1
USER root
COPY warm/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && rm /tmp/requirements.txt
USER 1000
