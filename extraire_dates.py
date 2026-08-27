import re
from datetime import datetime

MOIS = {
    'janvier':1,'fevrier':2,'février':2,'mars':3,'avril':4,'mai':5,'juin':6,
    'juillet':7,'aout':8,'août':8,'septembre':9,'octobre':10,'novembre':11,
    'decembre':12,'décembre':12
}

def _annee_pertinente(mois, jour):
    """Choisit l'annee a retenir pour un couple mois/jour sans annee explicite.

    Un client qui parle d'avril alors qu'on est en aout vise la saison
    suivante, pas celle qui vient de s'ecouler. On bascule donc sur l'annee
    suivante des que la date obtenue serait deja passee.
    """
    aujourdhui = datetime.now()
    annee = aujourdhui.year
    try:
        if datetime(annee, mois, jour) < aujourdhui.replace(
                hour=0, minute=0, second=0, microsecond=0):
            annee += 1
    except ValueError:
        # Jour invalide pour ce mois (31 fevrier) : on laisse l'annee courante,
        # l'appelant rejettera la date.
        pass
    return annee


def extraire_dates(texte):
    annee = datetime.now().year
    texte_lower = texte.lower()
    dates = []

    # Format "du 1 au 7 aout" ou "1 au 7 août"
    pattern = r'(\d{1,2})\s+au\s+(\d{1,2})\s+(' + '|'.join(MOIS.keys()) + r')'
    m = re.search(pattern, texte_lower)
    if m:
        j1, j2, mois_nom = int(m.group(1)), int(m.group(2)), m.group(3)
        mois = MOIS[mois_nom]
        # Meme annee pour les deux bornes, choisie sur la date d'arrivee.
        an = _annee_pertinente(mois, j1)
        dates.append(f"{an}-{mois:02d}-{j1:02d}")
        dates.append(f"{an}-{mois:02d}-{j2:02d}")
        return dates

    # Format JJ/MM ou JJ-MM
    pattern2 = r'(\d{1,2})[\/\-](\d{1,2})'
    matches = re.findall(pattern2, texte)
    for m in matches:
        try:
            jour, mois = int(m[0]), int(m[1])
            dates.append(f"{_annee_pertinente(mois, jour)}-{mois:02d}-{jour:02d}")
        except:
            pass
    if dates:
        return dates

    # Date seule en toutes lettres : "le 15 aout", "j'arrive le 3 juillet".
    # Le jour doit coller au nom du mois, ce qui evite d'attraper les nombres
    # sans rapport : "4 personnes en aout" ne matche pas.
    pattern3 = r'(\d{1,2})\s+(' + '|'.join(MOIS.keys()) + r')\b'
    m3 = re.search(pattern3, texte_lower)
    if m3:
        jour, mois = int(m3.group(1)), MOIS[m3.group(2)]
        if 1 <= jour <= 31:
            dates.append(f"{_annee_pertinente(mois, jour)}-{mois:02d}-{jour:02d}")

    return dates


def extraire_participants(texte):
    """Cherche le nombre d'adultes et l'age des enfants dans le message.

    Renvoie (nb_adultes, ages_enfants) ou (None, None) si le message ne
    donne pas de composition assez claire pour le parametre 'travelers' de
    SecureHoliday (ex: des enfants sont mentionnes mais sans age). Mieux
    vaut omettre le parametre que d'envoyer une composition fausse.
    """
    if not texte:
        return None, None
    bas = texte.lower()

    m_adultes = re.search(r'(\d+)\s*adultes?', bas)
    if not m_adultes:
        return None, None
    nb_adultes = int(m_adultes.group(1))

    ages_enfants = []
    for m in re.finditer(r'(\d+)?\s*enfants?\s+de\s+(\d+)\s*ans?', bas):
        nb = int(m.group(1)) if m.group(1) else 1
        ages_enfants.extend([int(m.group(2))] * nb)

    if 'enfant' in bas and not ages_enfants:
        return None, None

    return nb_adultes, ages_enfants


def extraire_type_hebergement(texte):
    """Devine si le client vise un emplacement ou une location, d'apres les mots employes."""
    if not texte:
        return None
    bas = texte.lower()
    if any(m in bas for m in ["tente", "caravane", "camping-car", "camping car", "emplacement"]):
        return "pitch"
    if any(m in bas for m in ["mobil-home", "mobilhome", "mobil home", "bungalow", "chalet", "location"]):
        return "accommodation"
    return None


# Catalogue transmis par Ctoutvert le 24/08/2026 (ShProductId). Les noms les
# plus specifiques sont places avant les plus generiques ("grand mobil home"
# avant "mobil home") pour qu'un match ne soit jamais ecrase par un autre
# plus large recherche ensuite.
PRODUITS = [
    ("grand mobil home", 124796),
    ("mobil home confort", 124793),
    ("mobil-home confort", 124793),
    ("tente safari", 94919),
    ("forfait randonneur", 81754),
    ("emplacement camping car", 79832),
    ("emplacement camping-car", 79832),
    ("emplacement camping", 79827),
    ("bengali", 79658),
    ("cyrus", 79659),
    ("mobil-home", 79661),
    ("mobilhome", 79661),
    ("mobil home", 79661),
]


def extraire_produit(texte):
    """Cherche le nom d'un hebergement precis du catalogue dans le message.

    Renvoie l'identifiant produit SecureHoliday (ShProductId) ou None si le
    client ne cite aucun nom du catalogue. Mieux vaut ne rien renvoyer que de
    pointer vers le mauvais hebergement.
    """
    if not texte:
        return None
    bas = texte.lower()
    for nom, produit_id in PRODUITS:
        if nom in bas:
            return produit_id
    return None
