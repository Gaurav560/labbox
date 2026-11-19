# labbox/ai-python: Python with the OpenAI and Anthropic SDKs, for labs with llm.enabled.
# The SDKs read OPENAI_BASE_URL / OPENAI_API_KEY (and the ANTHROPIC_ pair) that LabBox injects.
# Built with images/ as the context (see build_lab_images.sh) so it shares base/lab.
FROM labbox/python:v1
USER root
RUN pip install --no-cache-dir --break-system-packages openai==1.57.4 anthropic==0.42.0
COPY --chmod=755 base/lab /usr/local/bin/lab
USER 1000
