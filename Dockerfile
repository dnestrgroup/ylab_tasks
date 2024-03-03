FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_DEFAULT_TIMEOUT=100

ARG DOCKER_USER_ID=5001

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    locales \
    libfbclient2 && \
    useradd -m -u ${DOCKER_USER_ID} pyworker

USER ${DOCKER_USER_ID}

ADD --chown=${DOCKER_USER_ID}  ./requirements.txt .

ENV PATH "$PATH:/home/pyworker/.local/bin"

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ADD --chown=${DOCKER_USER_ID} . /app/
WORKDIR /app