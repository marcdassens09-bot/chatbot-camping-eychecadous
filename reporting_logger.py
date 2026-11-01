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
import os
from datetime import datetime, timedelta, timezone

# Durée de conservation : 12 mois (standard MP Solutions IA, RGPD).
CONSERVATION_JOURS = 365
_derniere_purge = {}


def _purger_anciens(log_path):
    """Supprime du fichier les événements de plus de CONSERVATION_JOURS.
    Au plus une fois par jour et par fichier, pour ne pas réécrire le
    fichier à chaque message."""
    aujourd_hui = datetime.now(timezone.utc).date()
    if _derniere_purge.get(log_path) == aujourd_hui:
        return
    _derniere_purge[log_path] = aujourd_hui
    limite = datetime.now(timezone.utc) - timedelta(days=CONSERVATION_JOURS)
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lignes = f.readlines()
    except FileNotFoundError:
        return
    gardees = []
    for ligne in lignes:
        try:
            if datetime.fromisoformat(json.loads(ligne)["timestamp"]) < limite:
                continue
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            pass  # ligne illisible : on la garde plutôt que de perdre une donnée
        gardees.append(ligne)
    if len(gardees) != len(lignes):
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(gardees)


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

    # La journalisation est un à-côté : si elle échoue (dossier /var/data
    # absent en local, disque plein, permissions...), le chat doit quand
    # même répondre au visiteur. On ne fait jamais planter la conversation
    # pour un problème de log.
    try:
        dossier = os.path.dirname(log_path)
        if dossier:
            os.makedirs(dossier, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        _purger_anciens(log_path)
    except OSError as e:
        print(f"[reporting_logger] Écriture du log impossible ({log_path}) : {e}")
