FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Mise à jour
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Rendre le script exécutable
RUN chmod +x /app/entrypoint.sh

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos '' django
USER django

EXPOSE 8000

# Entrypoint + commande par défaut
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]