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
