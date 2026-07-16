import re
from datetime import datetime

MOIS = {
    'janvier':1,'fevrier':2,'février':2,'mars':3,'avril':4,'mai':5,'juin':6,
    'juillet':7,'aout':8,'août':8,'septembre':9,'octobre':10,'novembre':11,
    'decembre':12,'décembre':12
}

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
        dates.append(f"{annee}-{mois:02d}-{j1:02d}")
        dates.append(f"{annee}-{mois:02d}-{j2:02d}")
        return dates

    # Format JJ/MM ou JJ-MM
    pattern2 = r'(\d{1,2})[\/\-](\d{1,2})'
    matches = re.findall(pattern2, texte)
    for m in matches:
        try:
            dates.append(f"{annee}-{int(m[1]):02d}-{int(m[0]):02d}")
        except:
            pass
    return dates
