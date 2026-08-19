# chatbot-camping-eychecadous

Chatbot du Camping Les Eychecadous (Artigat, 09130). **Sert campingartigat.com en production.**
Déployé sur Render : `chatbot-camping-eychecadous.onrender.com`. Branche `master`.

Ce service parle à de vrais clients. Tester en local avant tout déploiement.

## NE PAS réactiver calendar_service

L'import est commenté dans `app.py`, et cela doit le rester.

Audit du 03/08/2026 : l'agenda Google (`Camping Les Eychecadous`, compte de service
`chatbot-calendar@mp-solutions-ia-calendar`) est accessible mais contient **zéro événement,
toutes dates confondues**. Or `verifier_dispo()` renvoie `True` dès que l'agenda est vide.

Le rebrancher ferait donc annoncer « disponible » pour **toutes** les dates, à **tous** les
clients, sur 26 emplacements et 4 mobil-homes. Le code commenté protège le camping.

La source de vérité des réservations est **SecureHoliday**, pas Google Agenda.

## Comment le bot répond sur les disponibilités

Il n'affirme jamais de disponibilité. Il fournit un lien SecureHoliday pré-rempli :

| Message client | Lien produit |
|---|---|
| « du 15 au 22 août » | `search/product-list?dateStart=15/08/2026&dateEnd=22/08/2026` |
| « j'arrive le 15 août » | même chose sur 7 nuits par défaut, mention explicite au client |
| « des places en août ? » | `availabilities` — calendrier de la saison |

Le tunnel accepte `dateStart` / `dateEnd` en `JJ/MM/AAAA` url-encodé et affiche les
hébergements réellement libres avec leurs prix. Aucune clé API n'est nécessaire.
`nbAdults` n'est pas reconnu.

`extraire_dates()` bascule sur l'année suivante quand la date obtenue serait passée :
en août, « avril » vise avril prochain.

## Historique par visiteur (corrigé)

L'historique de chat est stocké dans `conversation_store`, un dict Python en mémoire
indexé par `session_id` (généré côté client, `sessionStorage`). Chaque visiteur a donc
son propre contexte — le bug de partage entre visiteurs simultanés est corrigé
(commit `ec72fcb fix: isole l'historique de chat par visiteur`).

`POST /effacer` (body `{"session_id": "..."}`) vide l'historique en mémoire d'une
session précise — sans authentification, et non appelée par le widget actuel (le
widget vide seulement l'affichage côté client via `postMessage`, le contexte serveur
reste intact). Utile pour purger une session de test après coup.

**Attention, purement en mémoire** : rien n'est persisté sur disque, donc un redéploiement
ou un redémarrage de l'instance efface tout l'historique de tous les visiteurs en cours.

## Mode ch'ti (remis en place le 19/08/2026)

Bouton "😉 Ch'ti" dans le header (`templates/index.html`) : bascule `modeChti`, envoyé
comme `chti: true/false` dans le body de `POST /chat`. Côté serveur, `INSTRUCTION_MODE_CHTI`
(dans `app.py`) est ajoutée à `PROMPT_SYSTEME_CAMPING` quand le flag est actif — le bot
répond alors en dialecte ch'ti/picard tout en gardant les informations exactes.

Fonctionnalité déjà présente début juillet (commits `df95734`, `608e8e3`) mais disparue
sans le vouloir lors de la refonte de la page (scène animée jour/nuit, commit `e2edaee`,
19/07/2026) qui a remplacé tout le HTML. Si elle disparaît à nouveau après une future
refonte de `templates/index.html`, chercher `chti-btn` / `INSTRUCTION_MODE_CHTI`.

## Reporting (ajouté 14/08/2026)

Système de reporting réutilisable MP Solutions IA : `reporting_logger.py` (log JSONL
à chaque échange), `reporting_stats.py`, `reporting_dashboard.py` (Blueprint Flask,
route `/reporting` protégée par mot de passe). Dashboard :
`chatbot-camping-eychecadous.onrender.com/reporting` — auth basique, utilisateur vide,
mot de passe = variable d'env `REPORTING_PASSWORD`.

Le disque persistant Render (`reporting-data`, mount `/var/data`) est requis pour que
les logs survivent aux redéploiements — le chemin dans l'appel `log_event()` doit
correspondre à ce mount path.

`detecter_escalade()` a été durci le 14/08/2026 : le prompt système excluait mal les
questions standard (dispo, tarifs) qui étaient parfois classées comme urgentes à tort.
Le prompt liste maintenant explicitement ce qui n'est jamais une escalade.

Reste à faire : reproduire l'intégration reporting sur chatbot-fumeco-leze (pas commencé).

### Purger une conversation de test de `chat_events.jsonl`

`log_event()` (`reporting_logger.py`) n'enregistre PAS le `session_id` — seulement
`timestamp`, `question` (déjà reformulée par `detecter_intention()`, donc différente du
message brut envoyé), `profile`, `urgent`, `answered`. Impossible de filtrer par session_id.

Procédure vérifiée le 19/08/2026, via le Shell Render (`chatbot-camping-eychecadous` →
onglet Shell) :
1. Identifier les lignes par leur texte reformulé et leur horodatage :
   `grep -n "mots du message" /var/data/chat_events.jsonl | cut -c1-80`
2. Supprimer par numéro de ligne : `sed -i '4,5d' /var/data/chat_events.jsonl`
3. Vérifier : `wc -l /var/data/chat_events.jsonl`, puis recharger `/reporting`.

Penser aussi à `POST /effacer` (session_id du test) pour vider le `conversation_store`
en mémoire — sinon le contexte de test reste dans l'historique de la session tant que
l'instance ne redémarre pas (mais n'apparaît nulle part de visible : ni dashboard, ni disque).

`questions_log.txt` et `escalades_log.txt` n'existent pas sur l'instance actuelle :
`enregistrer_question()` est un no-op (`return None`) et aucune escalade n'a encore été
déclenchée. Rien à purger de ce côté sauf si l'un des deux se met à exister un jour.

## Divers

- `print()` sans `flush` : les erreurs n'apparaissent pas dans les logs Render (stdout tamponné).
  Pour diagnostiquer, reproduire en local plutôt que chercher dans les logs.
- Le `.env` local contient un placeholder, pas une vraie clé.
- Beaucoup de code mort subsiste dans `app.py` (blocs après un `return`).
