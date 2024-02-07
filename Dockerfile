FROM python:latest as base
LABEL maintainer="DRKZ-CLINT"
LABEL repository="https://github.com/FREVA-CLINT/freva-storage-service.git"
ENV API_PORT=8080\
    API_WORKER=8\
    API_USERNAME=\
    API_PASSWORD=\
    MONGO_USERNAME=\
    MONGO_PASSWORD=\
    MONGO_HOST=\
    DEBUG=0
USER root
RUN set -e &&\
    mkdir -p /opt/app &&\
    groupadd -r --gid 1000 freva &&\
    mkdir -p /opt/storage-service &&\
    adduser --uid 1000 --gid 1000 --gecos "Default user" \
    --shell /bin/bash --disabled-password freva --home /opt/storage-service &&\
    chown -R freva:freva /opt/storage-service
FROM base as builder
COPY . /opt/app
WORKDIR /opt/app
RUN set -e &&\
    python3 -m ensurepip -U &&\
    python3 -m pip install -q flit &&\
    python3 -m flit build
FROM base as final
COPY --from=builder /opt/app/dist /opt/app/dist
RUN python3 -m pip install /opt/app/dist/freva_storage_service-*.whl
WORKDIR /opt/freva-storage-service
EXPOSE $API_PORT
USER freva
CMD ["python3", "-m", "freva_storage_service.cli"]
