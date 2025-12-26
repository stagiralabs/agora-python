FROM python:3.11-slim

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY pyproject.toml ./
COPY src ./src
COPY tests ./tests
COPY scripts ./scripts

RUN python -m pip install -U pip
RUN python -m pip install -e .
RUN chmod +x scripts/ci_local.sh

CMD ["bash", "scripts/ci_local.sh"]
