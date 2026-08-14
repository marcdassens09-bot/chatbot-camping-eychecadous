with open("app.py", "r", encoding="utf-8") as f:
    contenu = f.read()

nouvelles_fonctions = '''
def detecter_escalade(message, reponse_bot):
    try:
        resultat = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            system="""Tu analyses les echanges d\'un chatbot de camping francais.
Reponds UNIQUEMENT avec ce format JSON strict :
{"escalade": true/false, "niveau": "faible/moyen/eleve", "raison": "1 phrase max"}
Escalade = true si : client enerve, plainte, probleme technique repete, urgence.""",
            messages=[{"role": "user", "content": f"Message client : {message}\\nReponse bot : {reponse_bot}"}]
        )
        import json
        return json.loads(resultat.content[0].text.strip())
    except Exception:
        return {"escalade": False, "niveau": "faible", "raison": ""}

def enregistrer_escalade(message, niveau, raison):
    from datetime import datetime
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("escalades_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{horodatage} | NIVEAU:{niveau} | {raison} | MSG: {message[:100]}\\n")

def generer_rapport_hebdo():
    try:
        with open("questions_log.txt", "r", encoding="utf-8") as f:
            lignes = f.readlines()
        if not lignes:
            return "Aucune question enregistree cette semaine."
        questions = " | ".join([l.split(" | ")[-1].strip() for l in lignes[-50:]])
        resultat = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system="Analyse ces questions de clients d\'un camping francais. Genere un rapport : Top 3 sujets (%), ce qui marche, point a ameliorer, 1 conseil concret pour le gerant.",
            messages=[{"role": "user", "content": f"Questions : {questions}"}]
        )
        return resultat.content[0].text.strip()
    except Exception as e:
        return f"Erreur : {e}"

'''

route_rapport = """
@app.route("/rapport")
def rapport():
    cle = request.args.get("cle", "")
    if cle != os.environ.get("RAPPORT_CLE", "mpsolutions2026"):
        return jsonify({"erreur": "Acces refuse"}), 403
    return jsonify({"rapport": generer_rapport_hebdo()})

"""

contenu = contenu.replace('@app.route("/")\ndef index():', nouvelles_fonctions + '@app.route("/")\ndef index():')
contenu = contenu.replace('@app.route("/chat", methods=["POST"])', route_rapport + '@app.route("/chat", methods=["POST"])')

ancien = '        return jsonify({"reponse": texte})'
nouveau = '''        escalade = detecter_escalade(message_filtre, texte)
        if escalade.get("escalade"):
            enregistrer_escalade(message_filtre, escalade.get("niveau", "?"), escalade.get("raison", ""))
        return jsonify({"reponse": texte, "escalade": escalade.get("escalade", False), "niveau_escalade": escalade.get("niveau", "faible")})'''

if ancien in contenu:
    contenu = contenu.replace(ancien, nouveau)
    print("OK return modifie")
else:
    print("ERREUR pattern non trouve")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(contenu)
print("Patch termine")
