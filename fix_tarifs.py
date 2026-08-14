content = open('app.py', encoding='utf-8').read()
old = '- Tarifs mobil-homes et tentes lodge : voir reservation.secureholiday.net/fr/5438/'
new = """- Frais preparation et desinfection : 15 euros par sejour (obligatoire pour toute location)
=== TARIFS LOCATIONS (nuit / semaine) ===
- Bengali (max 4 personnes) : a partir de 45 euros/nuit ou 290 euros/semaine
- Cyrus (max 5-7 personnes) : a partir de 49 euros/nuit ou 310 euros/semaine
- Safari (max 5-7 personnes) : a partir de 55 euros/nuit ou 360 euros/semaine
- Mobil-home (max 4-6 personnes) : a partir de 55 euros/nuit ou 360 euros/semaine
- Mobil-home Confort climatise (max 4-6 personnes) : a partir de 60 euros/nuit ou 400 euros/semaine
- Mobil-home Grand Confort climatise (max 6-8 personnes) : a partir de 65 euros/nuit ou 450 euros/semaine
=== TARIFS SUPPLEMENTS ===
- Location draps lit double : 12 euros/semaine
- Location draps lit simple : 8 euros/semaine
- Location lit bebe : 10 euros/semaine
- Location refrigerateur : 3 euros/jour
- Kit serviettes de toilette : 5 euros/semaine
- Machine a laver : 4 euros
- Demi-pension : 25 euros/jour
- Recharge vehicule electrique 22KW : 5 euros"""
open('app.py', 'w', encoding='utf-8').write(content.replace(old, new))
print('OK !')
