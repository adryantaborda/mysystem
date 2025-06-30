# Imagem base com suporte a WeasyPrint e fontes
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependências de sistema necessárias pro WeasyPrint
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libpango1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    libpq-dev \
    curl \
    fonts-liberation && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos
COPY . /app/

# Instala dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Comando para iniciar o servidor (usando gunicorn)
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
