# -*- coding: utf-8 -*-
"""Fiche de demande : le chatbot transmet une demande complete par email.

Utilise l'API transactionnelle Brevo (HTTPS), pas le SMTP : le port 587 peut
etre bloque sur Render gratuit, l'API passe par le web classique.

Variables d'environnement (Render > Environment) :
    BREVO_API_KEY       cle API Brevo (obligatoire, cle "chatbot-camping")
    FICHE_DESTINATAIRE  adresse qui recoit les fiches
                        (defaut : contact@mpsolutionsia.fr, pour la phase de test)
    FICHE_EXPEDITEUR    adresse d'envoi verifiee dans Brevo
                        (defaut : contact@mpsolutionsia.fr)

Les coordonnees du client (email, telephone) ne passent JAMAIS par Claude :
filtrer_donnees_sensibles() les masque avant l'appel a l'API Anthropic. Elles
sont extraites ici du message brut, gardees en memoire par session, et
ajoutees a la fiche cote serveur.
"""

import html
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

BREVO_URL_ENVOI = "https://api.brevo.com/v3/smtp/email"
BREVO_URL_COMPTE = "https://api.brevo.com/v3/account"

# Memes motifs que filtrer_donnees_sensibles() dans app.py : ce qui est
# masque pour Claude est exactement ce qui est recupere ici pour la fiche.
MOTIF_EMAIL = r"[\w\.\-+]+@[\w\.\-]+\.\w+"
MOTIF_TELEPHONE = r"(?:\+33[\s.\-]?|\b0)[1-9](?:[\s.\-]?\d{2}){4}\b"

# Une session ne peut pas envoyer plus de fiches que ca (anti-abus).
MAX_FICHES_PAR_SESSION = 3

MOTIFS_LISIBLES = {
    "groupe": "Séjour de groupe",
    "demande_speciale": "Demande spéciale",
    "rappel": "Demande de rappel",
    "question_sans_reponse": "Question sans réponse du chatbot",
}


# ── Coordonnees ──────────────────────────────────────────────────────────────

def extraire_coordonnees(texte):
    """Retourne {'email': ..., 'telephone': ...} trouves dans le message brut."""
    resultat = {}
    if not texte:
        return resultat
    email = re.search(MOTIF_EMAIL, texte)
    if email:
        resultat["email"] = email.group(0).strip(".")
    tel = re.search(MOTIF_TELEPHONE, texte)
    if tel:
        chiffres = re.sub(r"[^\d+]", "", tel.group(0))
        if chiffres.startswith("+33"):
            chiffres = "0" + chiffres[3:]
        # Format lisible : 06 12 34 56 78
        resultat["telephone"] = " ".join(chiffres[i:i + 2] for i in range(0, 10, 2))
    return resultat


# ── Construction de la fiche ─────────────────────────────────────────────────

def construire_fiche(nom_client, motif, resume, coordonnees,
                     dates=None, nb_personnes=None, hebergement=None):
    """Retourne (sujet, html, texte) de l'email envoye au camping."""
    motif_lisible = MOTIFS_LISIBLES.get(motif, "Demande")
    lignes = [
        ("Client", nom_client),
        ("Téléphone", coordonnees.get("telephone")),
        ("Email", coordonnees.get("email")),
        ("Motif", motif_lisible),
        ("Dates", dates),
        ("Personnes", str(nb_personnes) if nb_personnes else None),
        ("Hébergement", hebergement),
    ]
    lignes = [(k, v) for k, v in lignes if v]

    sujet = f"[Chatbot camping] {motif_lisible} - {nom_client}"

    texte = "Nouvelle demande transmise par le chatbot du camping\n\n"
    texte += "\n".join(f"{k} : {v}" for k, v in lignes)
    texte += f"\n\nDemande :\n{resume}\n\n"
    texte += "Le client a confirmé vouloir transmettre cette demande.\n"
    texte += "-- Assistant MP Solutions IA"

    # Tout ce qui vient du client est echappe : pas de HTML injecte dans le mail.
    e = html.escape
    rangees = "".join(
        f'<tr><td style="padding:6px 12px;color:#E8730A;font-weight:bold;'
        f'white-space:nowrap;vertical-align:top;width:110px">{e(k)}</td>'
        f'<td style="padding:6px 12px;color:#1b3a2b">{e(v)}</td></tr>'
        for k, v in lignes
    )
    corps = (
        '<div style="font-family:Arial,sans-serif;max-width:560px;color:#1b3a2b">'
        '<h2 style="color:#E8730A;margin:0 0 4px">Nouvelle demande</h2>'
        '<p style="margin:0 0 16px;color:#555">Transmise par le chatbot du '
        'Camping Les Eychecadous</p>'
        f'<table style="border-collapse:collapse;width:100%;background:#f7f7f2">{rangees}</table>'
        '<h3 style="color:#E8730A;margin:20px 0 6px">Demande</h3>'
        f'<p style="white-space:pre-wrap;margin:0">{e(resume)}</p>'
        '<p style="margin:20px 0 0;font-size:12px;color:#888">Le client a confirmé '
        'vouloir transmettre cette demande. Répondre à ce mail écrit directement '
        'au client s\'il a donne son email.<br>Assistant MP Solutions IA</p>'
        '</div>'
    )
    return sujet, corps, texte


# ── Envoi Brevo ──────────────────────────────────────────────────────────────

def _appel_brevo(url, payload=None, timeout=10):
    cle = (os.environ.get("BREVO_API_KEY") or "").strip()
    if not cle:
        raise RuntimeError("BREVO_API_KEY absente des variables d'environnement")
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method="POST" if payload is not None else "GET",
        headers={
            "api-key": cle,
            "accept": "application/json",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as rep:
        return rep.status, rep.read().decode("utf-8", "replace")


def envoyer_fiche(sujet, corps_html, corps_texte, email_client=None):
    """Envoie la fiche. Retourne True si Brevo l'a acceptee."""
    expediteur = os.environ.get("FICHE_EXPEDITEUR", "contact@mpsolutionsia.fr")
    destinataire = os.environ.get("FICHE_DESTINATAIRE", "contact@mpsolutionsia.fr")
    payload = {
        "sender": {"name": "Chatbot Camping Les Eychecadous", "email": expediteur},
        "to": [{"email": destinataire}],
        "subject": sujet,
        "htmlContent": corps_html,
        "textContent": corps_texte,
    }
    if email_client:
        payload["replyTo"] = {"email": email_client}
    try:
        statut, _ = _appel_brevo(BREVO_URL_ENVOI, payload)
        print(f"[fiche] envoyee a {destinataire} (HTTP {statut})", flush=True)
        return 200 <= statut < 300
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        print(f"[fiche] ERREUR Brevo HTTP {e.code} : {detail}", flush=True)
    except Exception as e:
        print(f"[fiche] ERREUR envoi : {e}", flush=True)
    return False


# ── Garder la cle active (Brevo la coupe apres 90 jours sans usage) ──────────

_INTERVALLE_PING = 7 * 24 * 3600  # une fois par semaine
_dernier_ping = 0.0
_verrou_ping = threading.Lock()


def maintenir_cle_active():
    """Appel leger a Brevo au plus une fois par semaine, en arriere-plan.

    A appeler a chaque requete : ne fait rien si le dernier appel date de
    moins de 7 jours. Apres un redemarrage de l'instance, le premier visiteur
    declenche un appel (sans consequence).
    NB : non verifie que Brevo compte un simple GET /account comme
    "activite" de la cle. A controler dans Brevo > SMTP et API.
    """
    global _dernier_ping
    with _verrou_ping:
        if time.time() - _dernier_ping < _INTERVALLE_PING:
            return
        _dernier_ping = time.time()

    def _ping():
        try:
            statut, _ = _appel_brevo(BREVO_URL_COMPTE)
            print(f"[brevo] cle active, ping OK (HTTP {statut})", flush=True)
        except Exception as e:
            print(f"[brevo] ping echoue : {e}", flush=True)

    threading.Thread(target=_ping, daemon=True).start()


# ── Outil pour la boucle d'agent ─────────────────────────────────────────────

OUTIL_TRANSMETTRE = {
    "name": "transmettre_demande",
    "description": (
        "Transmet par email a l'equipe du camping une demande que le chatbot ne "
        "peut pas traiter seul : sejour de groupe, demande speciale, demande de "
        "rappel, question sans reponse. A appeler UNIQUEMENT apres avoir "
        "recapitule la demande au client ET obtenu son accord explicite. "
        "Les coordonnees du client sont ajoutees automatiquement cote serveur "
        "(elles apparaissent masquees dans la conversation, c'est normal)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "nom_client": {"type": "string", "description": "Nom donne par le client"},
            "motif": {"type": "string", "enum": list(MOTIFS_LISIBLES.keys())},
            "resume": {"type": "string",
                       "description": "La demande, claire et complete, en 2 a 5 phrases"},
            "dates": {"type": "string", "description": "Dates souhaitees, si connues"},
            "nb_personnes": {"type": "integer", "minimum": 1},
            "hebergement": {"type": "string",
                            "description": "Type d'hebergement souhaite, si connu"},
        },
        "required": ["nom_client", "motif", "resume"],
    },
}


def transmettre_demande(contacts_session, compteur_session, nom_client, motif,
                        resume, dates=None, nb_personnes=None, hebergement=None):
    """Implementation de l'outil. Retourne une chaine JSON pour le modele.

    contacts_session : dict {'email', 'telephone'} accumule pour la session.
    compteur_session : dict {'fiches': n} pour limiter les envois.
    """
    if not (contacts_session.get("telephone") or contacts_session.get("email")):
        return json.dumps({
            "ok": False,
            "erreur": "Aucune coordonnee recue. Demande au client son numero de "
                      "telephone ou son email avant de transmettre.",
        })
    if compteur_session.get("fiches", 0) >= MAX_FICHES_PAR_SESSION:
        return json.dumps({
            "ok": False,
            "erreur": "Limite de demandes atteinte pour cette conversation. "
                      "Invite le client a appeler le 05 67 44 51 65.",
        })
    sujet, corps_html, corps_texte = construire_fiche(
        nom_client, motif, resume, contacts_session, dates, nb_personnes, hebergement)
    if envoyer_fiche(sujet, corps_html, corps_texte, contacts_session.get("email")):
        compteur_session["fiches"] = compteur_session.get("fiches", 0) + 1
        return json.dumps({"ok": True, "message": "Demande transmise a l'equipe."})
    return json.dumps({
        "ok": False,
        "erreur": "L'envoi a echoue. Ne dis PAS que la demande est transmise. "
                  "Invite le client a appeler le 05 67 44 51 65 ou a ecrire a "
                  "campingartigat@gmail.com.",
    })
