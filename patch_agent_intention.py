import re

with open("app.py", "r", encoding="utf-8") as f:
    contenu = f.read()

# La nouvelle fonction à ajouter après les imports
fonction_agent = '''
def detecter_intention(message_brut):
    """Agent détecteur d'intention : clarifie le message avant de l'envoyer au chatbot."""
    try:
        resultat = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system="""Tu es un agent de clarification pour le chatbot du Camping Les Eychecadous.
Tu reçois un message client brut (avec fautes, abréviations, formulation floue).
Réponds UNIQUEMENT avec une phrase claire et complète qui reformule la demande.
Exemple : "c ki pour 2 adultes 1 gamin aout" → "Quel est le tarif pour 2 adultes et 1 enfant en août ?"
Ne réponds jamais à la question. Reformule seulement.""",
            messages=[{"role": "user", "content": f"Message client : {message_brut}"}]
        )
        return resultat.content[0].text.strip()
    except Exception:
        return message_brut  # Si l\'agent plante, on garde le message original

'''

# Insérer la fonction juste avant @app.route("/")
contenu = contenu.replace('@app.route("/")\ndef index():', fonction_agent + '@app.route("/")\ndef index():')

# Dans la route /chat, remplacer la ligne message_filtre par la version avec agent
ancien = 'message_filtre = filtrer_donnees_sensibles(message)'
nouveau = '''message_clarifie = detecter_intention(message)
    message_filtre = filtrer_donnees_sensibles(message_clarifie)'''
contenu = contenu.replace(ancien, nouveau)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(contenu)

print("✅ Patch appliqué — agent détecteur d'intention intégré.")
