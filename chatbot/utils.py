import requests
from django.conf import settings
from ddgs import DDGS
from io import BytesIO
import logging
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from pdfminer.high_level import extract_text
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

def _normalize_host(host: str) -> str:
    """Assure que host contient un schéma (http:// ou https://)."""
    if not host:
        return "http://localhost:11434"
    test = host.strip()
    if not test.startswith(("http://", "https://")):
        test = "http://" + test
    return test


class Action:
    def __init__(self,message):
        self.message=message
        pass
    def execute(selft,params:Dict[str,Any])-> Dict[str,Any]:
         """
        Exécute l’action et retourne :
        {
          "status": "success" | "error",
          "message": "..."
        }
        """
    pass

class ActionSendMail(Action):
    def __init__(self, message):
        super().__init__(message)
        
    def execute(selft, params):
        """
       Exécute l’action d’envoi d’un email.

    Args:
      self: Instance de l’action.
      params (dict): Dictionnaire contenant les informations de l’email :
        - to (str): Adresse email du destinataire
        - subject (str): Sujet de l’email
        - message (str): Contenu du message

    Returns:
        dict: Résultat de l’exécution de l’action :
        - status (str): "success" ou "error"
        - message (str): Message de confirmation ou d’erreur

    Raises:
    Exception: Levée si l’envoi de l’email échoue.
    """

        try:
            # comment: 
            msg =EmailMessage()
            msg["from"]="gihamos@gmail.com"
            msg["To"] = params["to"]
            msg["Subject"] = params["subject"]
            msg.set_content(params["message"])
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
             smtp.login("gihamos@gmail.com", "@Gihamos#0013")
             smtp.send_message(msg)
        except Exception as e:
            raise e
        # end try
        return super().execute(params)


def call_ollama_chat(messages: List[Dict[str, Any]], model: str, timeout: int = 120) -> Optional[str]:
    """
    Appelle l'API HTTP d'Ollama via /api/chat (non stream).
    Retourne le champ message.content (str) ou None en cas d'erreur.
    """
    raw_host = getattr(settings, "OLLAMA_HOST", "http://localhost:11434")
    host = _normalize_host(raw_host)
    url = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    logger.debug("Ollama call URL=%s payload=%s", url, payload)

    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        resp = session.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.InvalidSchema as e:
        # Erreur typique si l'URL n'a pas de scheme
        logger.exception("Invalid URL/schema pour Ollama: %s (raw_host=%s) — %s", url, raw_host, e)
        return None
    except requests.exceptions.RequestException as e:
        logger.exception("Erreur lors de l'appel à Ollama: %s", e)
        return None

    try:
        data = resp.json()
    except ValueError:
        logger.error("Réponse non JSON d'Ollama: %s", resp.text[:1000])
        return None

    content = data.get("message", {}).get("content")
    if content is None:
        logger.warning("Réponse Ollama inattendue: %s", data)
    else:
        logger.debug("Réponse reçue (len=%d)", len(content) if isinstance(content, str) else 0)

    return content




def extract_text_from_pdf(uploaded_file):
    """
    cette fonction permet extraire le texte contenu dans le pdf 
    """
    try:
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        text = extract_text(BytesIO(pdf_bytes))
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Erreur extraction PDF: {e}")


def web_search(query: str, max_results: int = 5) -> str:
    """
    Fait une petite recherche DuckDuckGo et retourne un résumé texte.
    """
    results_text = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            results_text.append(f"- {title}\n  {body}\n  ({href})")

    if not results_text:
        return "Aucun résultat pertinent trouvé."

    return "Voici quelques résultats issus du web :\n\n" + "\n\n".join(results_text)



def list_ollama_models():
    """
    Retourne la liste des modèles disponibles dans Ollama (via /api/tags).
    """
    raw_host = getattr(settings, "OLLAMA_HOST", "http://localhost:11434")
    host = raw_host.rstrip("/")
    host=_normalize_host(host)
    url = f"{host}/api/tags"

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel à Ollama /api/tags: {e}")
        return []

    try:
        data = resp.json()
    except ValueError:
        print(f"Réponse non JSON: {resp.text[:500]}")
        return []

    models = data.get("models", [])

    return [m.get("name") for m in models if m.get("name")]










