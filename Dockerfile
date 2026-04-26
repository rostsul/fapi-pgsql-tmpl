FROM python:3.14-slim AS builder
WORKDIR /app
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV UV_EXTRA_INDEX_URL=https://pypi.org/simple/
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -e ".[dev]"

FROM python:3.14-slim
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY src/ src/
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ready || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
