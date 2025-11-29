FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le projet (y compris entrypoint.sh)
COPY . .

# Rendre le script exécutable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# On passe par l'entrypoint
CMD ["/app/entrypoint.sh"]
