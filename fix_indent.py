"""
fix_indent.py — corrige l'indentation du bloc log_event() dans app.py
À lancer une seule fois : python fix_indent.py
"""
import re

with open("app.py", "r", encoding="utf-8") as f:
    contenu = f.read()

bloc_correct = (
    '        log_event(\n'
    '            log_path="chat_events.jsonl",\n'
    '            question=message_filtre,\n'
    '            urgent=escalade.get("escalade", False),\n'
    '            answered=bool(texte),\n'
    '            client_name="Camping Les Eychecadous",\n'
    '        )\n'
    '        if texte:'
)

pattern = re.compile(
    r'[ \t]*log_event\([ \t]*\n'
    r'[ \t]*log_path="chat_events\.jsonl",[ \t]*\n'
    r'[ \t]*question=message_filtre,[ \t]*\n'
    r'[ \t]*urgent=escalade\.get\("escalade", False\),[ \t]*\n'
    r'[ \t]*answered=bool\(texte\),[ \t]*\n'
    r'[ \t]*client_name="Camping Les Eychecadous",[ \t]*\n'
    r'[ \t]*\)[ \t]*\n'
    r'[ \t]*if texte:'
)

nouveau_contenu, n = pattern.subn(bloc_correct, contenu)

if n == 0:
    print("ERREUR : le bloc log_event() n'a pas été trouvé. Aucune modification faite.")
    print("Vérifie que tu as bien collé le bloc log_event() avant 'if texte:' dans app.py.")
elif n > 1:
    print(f"ATTENTION : {n} occurrences trouvées, une seule attendue. Aucune modification faite par sécurité.")
else:
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(nouveau_contenu)
    print("OK : indentation corrigée avec succès.")
