# -*- coding: utf-8 -*-
"""Outils de calcul de tarif pour le chatbot du Camping Les Eychecadous.

Le bot les appelle via la boucle d'agent de app.py (tool use) : le prix
est calcule par ce code Python, jamais "de tete" par le modele.

Les montants reprennent EXACTEMENT la grille du prompt systeme de app.py
(section TARIFS EMPLACEMENTS). Si la grille change, mettre a jour LES DEUX.
Ne couvre que les emplacements : pour les locations (mobil-homes,
bungalows), les prix sont "a partir de" et dependent de la saison — le bot
renvoie vers la page de reservation SecureHoliday.
"""

import json
from datetime import date


def calculer_nombre_nuits(date_arrivee: str, date_depart: str) -> str:
    arrivee = date.fromisoformat(date_arrivee)
    depart = date.fromisoformat(date_depart)
    nuits = (depart - arrivee).days
    if nuits <= 0:
        raise ValueError("La date de depart doit etre apres la date d'arrivee.")
    return json.dumps({"nombre_nuits": nuits})


def calculer_tarif_emplacement(
    nb_nuits: int,
    nb_adultes: int,
    nb_enfants_7_a_17: int = 0,
    nb_enfants_3_a_7: int = 0,
    nb_enfants_moins_3: int = 0,
    vehicules_supplementaires: int = 0,
    camping_car_services: bool = False,
) -> str:
    """Grille emplacements 2026 (voir prompt systeme de app.py)."""
    personnes_7_et_plus = nb_adultes + nb_enfants_7_a_17
    if nb_adultes < 1:
        raise ValueError("Il faut au moins un adulte.")
    if nb_nuits < 1:
        raise ValueError("Il faut au moins une nuit.")

    if personnes_7_et_plus == 1 and nb_enfants_3_a_7 == 0 and nb_enfants_moins_3 == 0:
        base = 11.00          # forfait randonneur (1 personne + 1 vehicule)
    else:
        base = 18.50          # forfait 2 personnes avec electricite

    supplement_personnes = (
        max(0, personnes_7_et_plus - 2) * 4.50
        + nb_enfants_3_a_7 * 3.50
        # moins de 3 ans : gratuit
    ) if base == 18.50 else 0.0

    par_nuit = base + supplement_personnes + vehicules_supplementaires * 2.50
    taxe_sejour = 0.86 * nb_adultes * nb_nuits          # +18 ans uniquement
    services = 5.00 if camping_car_services else 0.0     # eau + vidange, par sejour
    total = par_nuit * nb_nuits + taxe_sejour + services + 10.00  # + frais de dossier

    return json.dumps({
        "prix_par_nuit": round(par_nuit, 2),
        "taxe_sejour_totale": round(taxe_sejour, 2),
        "frais_dossier": 10.00,
        "services_camping_car": services,
        "total_sejour": round(total, 2),
        "detail": f"{nb_nuits} nuit(s) x {round(par_nuit, 2)} EUR "
                  f"+ taxe de sejour {round(taxe_sejour, 2)} EUR "
                  f"+ frais de dossier 10 EUR"
                  + (" + services camping-car 5 EUR" if camping_car_services else ""),
    })


OUTILS = [
    {
        "name": "calculer_nombre_nuits",
        "description": "Calcule le nombre de nuits entre deux dates de sejour. "
                       "A utiliser des que le client donne des dates plutot "
                       "qu'un nombre de nuits.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_arrivee": {"type": "string", "description": "Format AAAA-MM-JJ"},
                "date_depart": {"type": "string", "description": "Format AAAA-MM-JJ"},
            },
            "required": ["date_arrivee", "date_depart"],
        },
    },
    {
        "name": "calculer_tarif_emplacement",
        "description": "Calcule le prix exact d'un sejour en EMPLACEMENT "
                       "(tente, caravane, camping-car), taxe de sejour et "
                       "frais de dossier inclus. A utiliser pour TOUT calcul "
                       "de prix d'emplacement : ne jamais calculer de tete. "
                       "Ne concerne PAS les locations (mobil-homes, bungalows).",
        "input_schema": {
            "type": "object",
            "properties": {
                "nb_nuits": {"type": "integer", "minimum": 1},
                "nb_adultes": {"type": "integer", "minimum": 1,
                               "description": "18 ans et plus"},
                "nb_enfants_7_a_17": {"type": "integer"},
                "nb_enfants_3_a_7": {"type": "integer"},
                "nb_enfants_moins_3": {"type": "integer"},
                "vehicules_supplementaires": {"type": "integer",
                                              "description": "Vehicules au-dela du premier"},
                "camping_car_services": {"type": "boolean",
                                         "description": "Ajouter les services eau et vidange (5 EUR)"},
            },
            "required": ["nb_nuits", "nb_adultes"],
        },
    },
]

IMPLEMENTATIONS = {
    "calculer_nombre_nuits": calculer_nombre_nuits,
    "calculer_tarif_emplacement": calculer_tarif_emplacement,
}
