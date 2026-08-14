with open("app.py", "r", encoding="utf-8") as f:
    contenu = f.read()

import_twilio = "from twilio.rest import Client as TwilioClient\n"
if "twilio" not in contenu:
    contenu = import_twilio + contenu

fonction_whatsapp = '''
def envoyer_whatsapp_anthony(message):
    """Envoie une alerte WhatsApp à Anthony via Twilio."""
    try:
        import os
        twilio_client = TwilioClient(
            os.environ.get("TWILIO_ACCOUNT_SID"),
            os.environ.get("TWILIO_AUTH_TOKEN")
        )
        twilio_client.messages.create(
            from_="whatsapp:+14155238886",
            to=os.environ.get("ANTHONY_WHATSAPP"),
            body=message
        )
        print("WhatsApp envoyé à Anthony")
    except Exception as e:
        print(f"Erreur WhatsApp : {e}")

'''

contenu = contenu.replace(
    "def enregistrer_escalade(",
    fonction_whatsapp + "def enregistrer_escalade("
)

ancien = "        if escalade.get(\"escalade\"):\n            enregistrer_escalade(message_filtre, escalade.get(\"niveau\", \"?\"), escalade.get(\"raison\", \"\"))"
nouveau = """        if escalade.get("escalade"):
            enregistrer_escalade(message_filtre, escalade.get("niveau", "?"), escalade.get("raison", ""))
            niveau = escalade.get("niveau", "faible")
            raison = escalade.get("raison", "")
            msg_anthony = f"🚨 ALERTE CHATBOT CAMPING\\nNiveau : {niveau}\\nRaison : {raison}\\nMessage client : {message_filtre[:100]}"
            envoyer_whatsapp_anthony(msg_anthony)"""

contenu = contenu.replace(ancien, nouveau)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(contenu)

print("Patch WhatsApp terminé")
