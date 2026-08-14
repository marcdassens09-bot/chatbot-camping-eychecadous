"""
reporting_logger.py — MP Solutions IA
Module réutilisable à copier dans chaque projet client
(chatbot-fumeco-leze, chatbot-camping-eychecadous, etc.)

Utilisation dans app_XXX.py :

    from reporting_logger import log_event

    log_event(
        log_path="fumeco_chat.log",
        question="Vous livrez le samedi ?",
        profile="particulier",
        urgent=False,
        answered=True,
    )
"""

import json
from datetime import datetime, timezone


def log_event(log_path, question, profile="inconnu", urgent=False,
               answered=True, client_name=None):
    """
    Écrit un événement de conversation dans le fichier de log JSONL.
    À appeler après chaque échange avec un visiteur, en plus (ou à la
    place) du log texte actuel.

    Args:
        log_path: chemin du fichier .log (ex: "fumeco_chat.log")
        question: la question posée par le visiteur
        profile: "particulier" / "pro_distribution" / "pro_chantier" /
                 "pro" / "inconnu" — adapte les valeurs à ton tri de
                 visiteurs (voir tes prompts système)
        urgent: True si le message a déclenché une alerte urgence
        answered: True si le bot a répondu, False si prise de message
        client_name: nom du client, utile si plusieurs bots partagent
                      un même fichier de log
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": (question or "")[:500],
        "profile": profile,
        "urgent": bool(urgent),
        "answered": bool(answered),
    }
    if client_name:
        event["client"] = client_name

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
