# labbox/langchain: Python 3.12 with LangChain 1.5 and everything the course uses, installed at build time so
# chapters and checks work offline. requirements.txt pins every package (see warm/requirements.in).
FROM labbox/ai-python:v1
USER root
COPY warm/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages --ignore-installed -r /tmp/requirements.txt && rm /tmp/requirements.txt
# tiktoken downloads its encodings on first use: fetch them now, into a folder every user can read.
ENV TIKTOKEN_CACHE_DIR=/opt/tiktoken
RUN mkdir -p /opt/tiktoken && python3 -c "import tiktoken; [tiktoken.get_encoding(e) for e in ('o200k_base', 'cl100k_base')]" \
    && chmod -R a+rX /opt/tiktoken
USER 1000
