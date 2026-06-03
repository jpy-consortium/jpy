# syntax=docker/dockerfile:1.4

ARG PYTHON_TAG
FROM python:${PYTHON_TAG} as build

ARG DEBIAN_FRONTEND="noninteractive"
ARG TARGETARCH
ARG PYTHON_TAG
RUN \
    --mount=type=cache,target=/var/cache/apt,sharing=locked,id=apt-${TARGETARCH}-${PYTHON_TAG} \
    --mount=type=cache,target=/var/lib/apt,sharing=locked,id=apt-${TARGETARCH}-${PYTHON_TAG} \
    set -eux; \
    rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' | tee /etc/apt/apt.conf.d/keep-cache; \
    echo 'Acquire::Retries "3";'           >  /etc/apt/apt.conf.d/80-retries; \
    echo 'Acquire::Retries::Delay "true";'  >> /etc/apt/apt.conf.d/80-retries; \
    echo 'Acquire::http::Timeout "30";'     >> /etc/apt/apt.conf.d/80-retries; \
    echo 'Acquire::https::Timeout "30";'    >> /etc/apt/apt.conf.d/80-retries; \
    wget --no-hsts --tries=3 --waitretry=5 --retry-connrefused --timeout=10 \
         -O /usr/share/keyrings/adoptium.asc https://packages.adoptium.net/artifactory/api/gpg/key/public; \
    echo "deb [signed-by=/usr/share/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list; \
    apt-get -qq update; \
    apt-get -qq -y --no-install-recommends install temurin-11-jdk maven
RUN \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    set -eux; \
    python -m venv /jpy-build-venv; \
    /jpy-build-venv/bin/pip install --upgrade pip setuptools; \
    /jpy-build-venv/bin/pip install --only-binary=:all: wheel patchelf
ENV JAVA_HOME=/usr/lib/jvm/temurin-11-jdk-${TARGETARCH} \
    VIRTUAL_ENV='/jpy-build-venv' \
    PATH="/jpy-build-venv/bin:${PATH}" \
    CI=true
COPY --link . /jpy
RUN \
  --mount=type=cache,target=/root/.m2,sharing=locked \
  cd /jpy; \
  .github/env/Linux/bdist-wheel.sh

FROM scratch
COPY --link --from=build /jpy/dist/* .
