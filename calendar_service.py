from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
KEY_FILE = os.environ.get("GOOGLE_CALENDAR_KEY_PATH", "/etc/secrets/google_calendar_key.json") if os.path.exists("/etc/secrets/google_calendar_key.json") else os.path.join(os.path.dirname(__file__), "google_calendar_key.json")
CALENDAR_ID = '431c633f0ab763af31481ce621e1c4b9c9ee2ba511888c0107e7ebeda4ed2034@group.calendar.google.com'

def get_service():
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def verifier_dispo(date_debut, date_fin):
    """Vérifie si le créneau est libre. date_debut/date_fin au format 'YYYY-MM-DD'"""
    service = get_service()
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=date_debut + 'T00:00:00+02:00',
        timeMax=date_fin + 'T23:59:59+02:00',
        singleEvents=True,
    ).execute()
    return len(events.get('items', [])) == 0

def creer_reservation(nom, email, date_debut, date_fin, nb_personnes):
    """Crée un événement de réservation dans le calendrier"""
    service = get_service()
    event = {
        'summary': f'Reservation - {nom} ({nb_personnes} pers.)',
        'description': f'Email: {email}\nPersonnes: {nb_personnes}',
        'start': {'date': date_debut, 'timeZone': 'Europe/Paris'},
        'end':   {'date': date_fin,   'timeZone': 'Europe/Paris'},
    }
    result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return result.get('id')

def get_reservations_mois(annee, mois):
    """Retourne toutes les réservations d'un mois donné"""
    service = get_service()
    debut = f'{annee}-{mois:02d}-01'
    fin   = f'{annee}-{mois:02d}-28'
    events = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=debut + 'T00:00:00+02:00',
        timeMax=fin   + 'T23:59:59+02:00',
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    return events.get('items', [])

if __name__ == '__main__':
    # Test rapide
    dispo = verifier_dispo('2026-08-01', '2026-08-07')
    print(f"Disponible du 1 au 7 août : {'OUI' if dispo else 'NON'}")
    reservations = get_reservations_mois(2026, 8)
    print(f"Réservations en août : {len(reservations)}")
