FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && groupadd -g 10001 aurs && useradd -u 10001 -g 10001 -s /usr/sbin/nologin aurs && mkdir -p /data && chown aurs:aurs /data
COPY app.py start.py /app/
COPY web /app/web
COPY scripts /app/scripts
USER 10001:10001
ENV PORT=8000 AURS_DATA_DIR=/data
EXPOSE 8000
CMD ["python","start.py"]
