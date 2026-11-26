# labbox/forward-deployed-engineer: Python 3.12, the OpenAI SDK (from labbox/ai-python), FastAPI, httpx, pydantic and
# pytest, installed at build time so chapters and checks work offline. requirements.txt pins every package.
FROM labbox/ai-python:v1
USER root
COPY warm/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages --ignore-installed -r /tmp/requirements.txt && rm /tmp/requirements.txt
USER 1000
