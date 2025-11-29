#!/bin/sh
set -e

echo "📦 Migrations Django..."
python manage.py migrate --noinput

python << 'EOF'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or ""
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

print("👤 Vérification / création du superuser...")

if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' créé.")
    else:
        print(f"ℹ️ Superuser '{username}' existe déjà, pas de création.")
else:
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(username="admin", email="admin@chabot.info", password="admin")
        print("✅ SuperUser par défaut créé => username: admin / email: admin@chabot.info / password: admin")
    else:
        print("ℹ️ SuperUser par défaut existe déjà, pas de création.")
EOF

print( "🚀 Lancement de Gunicorn...")

exec gunicorn --bind 0.0.0.0:8000 config.wsgi
