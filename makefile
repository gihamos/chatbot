# Nom du projet
PROJECT_NAME=django_chatbot

# Commandes Docker Compose
up:
    docker-compose up --build -d

down:
    docker-compose down

logs:
    docker-compose logs -f

restart: down up

# Nettoyer les conteneurs et volumes
clean:
    docker-compose down -v
    docker system prune -f

# Réinitialiser la base SQLite
reset-db:
    rm -f db.sqlite3
    docker-compose run --rm django python manage.py migrate

# Créer un superuser manuellement
createsuperuser:
    docker-compose run --rm django python manage.py createsuperuser

# Lancer les tests Django
test:
    docker-compose run --rm django python manage.py test