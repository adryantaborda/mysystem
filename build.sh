#!/usr/bin/env bash
apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpango1.0-dev \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libgdk-pixbuf2.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    curl \
    libpq-dev \
    git \
    && pip install -r requirements.txt
