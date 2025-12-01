from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Conversation, Message
from .utils import call_ollama_chat, extract_text_from_pdf, web_search, list_ollama_models
import re


@login_required
def chat_view(request):
    user = request.user

    # Toutes les conversations de l'utilisateur (pour la liste à gauche/droite)
    conversations = Conversation.objects.filter(user=user).order_by("-created_at")

    # Conversation courante (en session)
    conv_id = request.session.get("conversation_id")
    conversation = None

    if conv_id:
        try:
            conversation = Conversation.objects.get(id=conv_id, user=user)
        except Conversation.DoesNotExist:
            conversation = None

    # Si aucune conversation n'existe, on en crée une nouvelle
    if conversation is None:
        conversation = Conversation.objects.create(user=user, title="Nouvelle conversation")
        request.session["conversation_id"] = conversation.id

    messages = conversation.messages.all()

    # Modèles Ollama
    try:
        available_models = list_ollama_models()
        if not available_models:
            available_models = [settings.DEFAULT_MODEL]
    except Exception:
        available_models = [settings.DEFAULT_MODEL]
        print("echec")

    current_model = request.session.get("current_model", available_models[0])

    context = {
        "conversation": conversation,
        "messages": messages,
        "available_models": available_models,
        "current_model": current_model,
        "conversations": conversations,                  
        "current_conversation_id": conversation.id,    
        "developer_name": "NGANGA YABIE Taïse De Thèse",
    }
    return render(request, "chat/chat.html", context)


def clean_model_answer(text: str) -> str:
    """
    Supprime les blocs <think>...</think> si le modèle en génère,
    et fait un petit strip.
    """
    if not text:
        return ""
    # supprime les blocs <think>...</think> (greedy)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


@login_required
@require_POST
def send_message(request):
    user = request.user

    # Récupération de la conversation active depuis la session
    conv_id = request.session.get("conversation_id")
    conversation = get_object_or_404(Conversation, id=conv_id, user=user)

    message = (request.POST.get("message") or "").strip()
    action = request.POST.get("action", "chat")
    model = request.POST.get("model")

    # Petite validation
    if not message and action == "chat":
        return JsonResponse({"error": "Le message est vide."}, status=400)

    # Reconstruction de l'historique pour l'envoyer au modèle
    history = []
    for msg in conversation.messages.all():
        history.append({
            "role": msg.role,
            "content": msg.content,
        })

    # On ajoutera éventuellement des messages "system" pour PDF / web
    extra_system_messages = []

    # 1) Si action = pdf → extraire le texte du PDF et l'ajouter au contexte
    if action == "pdf":
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "Aucun fichier PDF fourni."}, status=400)

        try:
            pdf_text = extract_text_from_pdf(uploaded_file)
        except Exception as e:
            return JsonResponse(
                {"error": f"Erreur lors de la lecture du PDF : {e}"},
                status=400
            )

        # on tronque un peu pour éviter un contexte trop lourd
        pdf_text_short = pdf_text[:10000]
        sys_msg = (
               "Contexte document PDF fourni par l'utilisateur.\n"
                    "=== Début du document ===\n"
                        f"{pdf_text_short}\n"
                    "=== Fin du document ===\n\n"
                 "Consigne: prends en compte  ce contenu pour répondre aux questions."
                    )
        extra_system_messages.append(sys_msg)

        # on sauvegarde pour garder la trace
        Message.objects.create(
            conversation=conversation,
            role="system",
            content=f"[PDF] {uploaded_file.name} intégré au contexte."
        )

    # 2) Si action = web → faire une recherche web et l'ajouter au contexte
    if action == "web":
        try:
            search_summary = web_search(message)
        except Exception as e:
            return JsonResponse(
                {"error": f"Erreur lors de la recherche web : {e}"},
                status=400
            )
        sys_msg = (
             f"Résultats de recherche web pour la requête « {message} » :\n"
            f"{search_summary}\n\n"
            "Consigne: Réponds en t'appuyant sur ces résultats."
            )

        extra_system_messages.append(sys_msg)

        Message.objects.create(
            conversation=conversation,
            role="system",
            content=f"[WEB] Résultats de recherche ajoutés pour : {message}"
        )

    # On ajoute les messages system dans l'historique envoyé au modèle
    for sys_text in extra_system_messages:
        history.append({"role": "system", "content": sys_text})

    # On ajoute le nouveau message utilisateur
    if message:
        history.append({"role": "user", "content": message})

    # On sauvegarde le message utilisateur dans la base
    if message:
        Message.objects.create(
            conversation=conversation,
            role="user",
            content=message,
        )

    # Appel à Ollama
    try:
        raw_answer = call_ollama_chat(history, model=model)
    except Exception as e:
        return JsonResponse(
            {"error": f"Erreur lors de l'appel au modèle : {e}"},
            status=500
        )

    answer = clean_model_answer(raw_answer)

    # On sauvegarde la réponse de l'IA
    Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=answer,
    )

    return JsonResponse({"answer": answer})


def register(request):
    """
    Page d'inscription utilisateur (username + mot de passe).
    """
    if request.user.is_authenticated:
        return redirect("chat")  # nom de ta vue de chat

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Compte créé avec succès, tu peux te connecter 🙂")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})

@login_required
def new_conversation(request):
    """
    Crée une nouvelle conversation vide et la rend active.
    """
    conversation = Conversation.objects.create(
        user=request.user,
        title="Nouvelle conversation"
    )
    request.session["conversation_id"] = conversation.id
    return redirect("chat")

@login_required
def switch_conversation(request, pk):
    """
    Passe sur une autre conversation appartenant à l'utilisateur.
    """
    conversation = get_object_or_404(Conversation, id=pk, user=request.user)
    request.session["conversation_id"] = conversation.id
    return redirect("chat")

@login_required
def delete_conversation(request, pk):
    """
    Supprime une conversation appartenant à l'utilisateur.
    Si c'était la conversation active, on en choisit une autre ou on en recrée une.
    """
    conversation = get_object_or_404(Conversation, id=pk, user=request.user)

    # On ne permet la suppression qu'en POST (sécurité)
    if request.method == "POST":
        conv_was_active = (request.session.get("conversation_id") == conversation.id)
        conversation.delete()

        # Si c'était la conv active, on en choisit une autre ou on en recrée une
        if conv_was_active:
            remaining = Conversation.objects.filter(user=request.user).order_by("-created_at").first()
            if remaining:
                request.session["conversation_id"] = remaining.id
            else:
                new_conv = Conversation.objects.create(user=request.user, title="Nouvelle conversation")
                request.session["conversation_id"] = new_conv.id

    return redirect("chat")
