# 🤖 Chatbot IA Django avec Ollama, PDF et Web Search

Ce projet est un chatbot intelligent développé avec **Django**, intégrant des modèles LLM via **Ollama**, capable d’analyser des documents PDF, de faire des recherches web, et de maintenir un historique conversationnel par utilisateur.  
Il est entièrement **conteneurisé avec Docker** et utilise **SQLite** comme base de données pour un déploiement simple et portable.

---

## 🚀 Fonctionnalités

- 🔗 **Intégration Ollama** : dialogue avec des modèles LLM locaux (`llama2`, `deepseek-v3.1`, etc.)
- 📄 **Analyse de PDF** : extraction automatique du texte et injection dans le contexte conversationnel
- 🌐 **Recherche Web** : résumé des résultats via DuckDuckGo (`ddgs`)
- 🧠 **Mémoire conversationnelle** : historique par utilisateur et par session
- 🐳 **Conteneurisation Docker** : déploiement simplifié avec `docker-compose`
- 🛠️ **Interface sécurisée** : authentification Django, gestion des utilisateurs
- 🗂️ **Base SQLite** : simple, légère et persistée via volume Docker

---

## 🧰 Technologies utilisées
<pre>
| Backend        | IA / NLP        | Extraction PDF     | Conteneurisation |
|----------------|------------------|---------------------|------------------|
| Django 4.x     | Ollama (LLM local) | PyPDF2 / pdfminer.six | Docker / Docker Compose |
| SQLite         | Modèles comme `llama2`, `deepseek-v3.1` | OCR optionnel (Tesseract) | Volumes persistants |
| ddgs (DuckDuckGo Search) | Historique structuré | Gestion des fichiers | Réseau interne |
</pre>
---

## 📦 Installation locale (sans Docker)

```bash
git clone https://github.com/gihamos/chatbot.git
cd chatbot

python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 🐳 Déploiement avec Docker + SQLite

1. Démarrer Ollama en local (hors conteneur)
  ```bash
  ollama serve
  ollama pull llama2
  ```
  Ollama doit être accessible sur [](http://ollama:11434)

2. Lancer l'application Django avec Docker
  ```bash
  docker-compose up --build -d
  ```
3. Accéder à l'application
   -  Interface web : [](http://localhost:8000)
   -  Admin Django : [](http://localhost:8000/admin)
     
## 📁 Structure du projet
<pre>

  chatbot/
├── core/              # App principale (vues, modèles, utils)
├── static/            # Fichiers statiques
├── media/             # Fichiers uploadés (PDF)
├── Dockerfile         # Image Django
├── docker-compose.yml # Services Django + Ollama
├── entrypoint.sh      # Script de démarrage (migrations + superuser)
├── requirements.txt   # Dépendances Python
├── Makefile           # Commandes simplifiées
└── manage.py

</pre>
## 🧪 Utilisation avec Makefile
-  Démarer l'app:
   ```bash
   make up
   ```
-  Arrêter:
  ```bash
     make down
  ```
-  Voir les logs:
  ```bash
     make logs
  ```
- Réinitialiser la base SQLite :
  ```bash
     make reset-db
  ```
- Créer un superuser :
  ```bash
     make createsuperuser
  ```
## ✅ À venir
-  Interface React ou Vue.js
-  Résumé automatique des PDF
-  Export des conversations
-  Support OCR conditionnel
  
## 📄 Licence
Ce projet est open-source sous licence MIT.

## 👤 Auteur
Taïse De Thèse NGANGA YABIE

##💼 Portfolio : 
[](https://gihamos.github.io/portofolio_taise)
