# labbox/rag-vector-databases: Python 3.12 with fastembed (local embedding and reranking models), FAISS, the Qdrant
# client and FastAPI, installed at build time so chapters and checks work offline. requirements.txt pins every
# package (see warm/requirements.in); the two models are downloaded into /opt/fastembed while building.
FROM labbox/ai-python:v1
USER root
COPY warm/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages --ignore-installed -r /tmp/requirements.txt && rm /tmp/requirements.txt
ENV FASTEMBED_CACHE_PATH=/opt/fastembed
COPY warm/warm_models.py /tmp/warm_models.py
RUN mkdir -p /opt/fastembed && python3 /tmp/warm_models.py && rm /tmp/warm_models.py && chmod -R a+rX /opt/fastembed
# The models are in the image: never try to download them again (the checks have no network).
ENV HF_HUB_OFFLINE=1
# A lab machine has 2 CPUs but sees every core of the host: without a limit, NumPy's and FAISS's thread pools start
# a thread per host core and fight over the two CPUs (a brute-force search took 44 ms instead of 7).
ENV OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
USER 1000
