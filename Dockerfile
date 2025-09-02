FROM python:3.12

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc g++ make && \
    apt-get clean

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock /app/

RUN uv sync --frozen

COPY . /app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
