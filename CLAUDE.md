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

## Défaut connu : historique partagé

`historique` est une variable globale (`global historique` dans `/chat`). Deux visiteurs
simultanés partagent la même conversation, et le message de l'un entre dans le contexte
envoyé pour l'autre. Correctif à faire : stockage par `session_id`, sur le modèle du
`conversation_store` de `agent-loop/mpsolutionsia_app.py`.

`POST /effacer` vide cet historique global — sans authentification.
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

## Divers

- `print()` sans `flush` : les erreurs n'apparaissent pas dans les logs Render (stdout tamponné).
  Pour diagnostiquer, reproduire en local plutôt que chercher dans les logs.
- Le `.env` local contient un placeholder, pas une vraie clé.
- Beaucoup de code mort subsiste dans `app.py` (blocs après un `return`).
