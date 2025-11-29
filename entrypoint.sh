#!/bin/sh
set -e

echo "📦 Migrations Django..."
python manage.py migrate --noinput

python << 'EOF'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
import logging
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

logger.info("👤 Vérification / création du superuser...")

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or ""
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
         logger.info(f"✅ Superuser '{username}' créé.")
    else:
          logger.warning(f"ℹ️ Superuser '{username}' existe déjà, pas de création.")
else:
    User.objects.create_superuser(username="admin", email=admin@chabot.info, password="admin")
     logger.info(f" ============================\n✅  identifiant SuperUser par defaut  créée => \n username: admin \n email: admin@chabot.info \n password : admin \n ======================\n")

logger.info( "🚀 Lancement de Gunicorn...")
EOF

exec gunicorn --bind 0.0.0.0:8000 config.wsgi
