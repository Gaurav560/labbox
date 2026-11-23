# labbox/langgraph: the LangChain image (Python 3.12, LangChain 1.5.2, LangGraph 1.2.24, all pinned) plus Deep Agents
# and the SQLite checkpointer, installed at build time so chapters and checks work offline.
FROM labbox/langchain:v1
USER root
COPY warm/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages --no-deps -r /tmp/requirements.txt && rm /tmp/requirements.txt
USER 1000
