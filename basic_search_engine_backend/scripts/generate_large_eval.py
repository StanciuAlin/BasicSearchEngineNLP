import json
import random

# Liste extinse pentru diversificare maximă
subiecte = [
    "whale", "ship", "sea", "captain", "ocean", "harpoon", "adventure",
    "navigation", "storm", "crew", "vessel", "whaleboat", "anchor", "deck",
    "voyage", "map", "compass", "island", "shore", "depths", "waves",
    "mast", "sail", "horizon", "legend", "monster", "treasure", "coast",
    "lighthouse", "tide", "marine", "expedition", "discovery", "myth"
]

personaje = [
    "Ahab", "Ishmael", "Queequeg", "Starbuck", "Pip", "Mapple", "Stubb",
    "Flask", "Fedallah", "Tashtego", "Daggoo", "Bildad", "Peleg", "Boone",
    "Nemo", "Crusoe", "Silver", "Jim", "Gulliver", "Marlow", "Kurtz"
]

actiuni = [
    "hunting", "sailing", "searching", "fighting", "observing", "tracking",
    "escaping", "exploring", "conquering", "surviving", "navigating",
    "challenging", "mapping", "studying", "describing", "recounting"
]

adjective = [
    "white", "giant", "dangerous", "mysterious", "ancient", "savage",
    "infinite", "dark", "golden", "forgotten", "spectral", "ruthless",
    "majestic", "silent", "furious", "uncharted", "frozen", "tropical",
    "terrible", "mighty", "lone", "broken", "stormy", "calm"
]

locatii = [
    "Pacific", "Atlantic", "Indian Ocean", "Nantucket", "London",
    "Arctic", "Antarctic", "Caribbean", "South Seas", "open water"
]

queries = []

# Generăm 1000 de combinații cu structuri variate
for i in range(1, 1001):
    # Inițializăm q_text cu un șir vid sau o valoare default
    q_text = ""

    # Alegem aleatoriu un tip de query pentru diversitate structurală
    structura = random.choice([
        "keyword", "description", "person_action", "full_sentence", "geographic"
    ])

    if structura == "keyword":
        # Ex: "mysterious white whale"
        q_text = f"{random.choice(adjective)} {random.choice(adjective)} {random.choice(subiecte)}"

    elif structura == "description":
        # Ex: "hunting the dangerous giant"
        q_text = f"{random.choice(actiuni)} the {random.choice(adjective)} {random.choice(subiecte)}"

    elif structura == "person_action":
        # Ex: "Captain Ahab sailing the Pacific"
        q_text = f"Captain {random.choice(personaje)} {random.choice(actiuni)} the {random.choice(locatii)}"

    elif structura == "full_sentence":
        # Ex: "What is the legend of the ancient ship?"
        q_text = f"What is the {random.choice(subiecte)} of the {random.choice(adjective)} {random.choice(subiecte)}?"

    elif structura == "geographic":
        # Ex: "Storm in the South Seas"
        q_text = f"{random.choice(subiecte).capitalize()} in the {random.choice(locatii)}"

    # Adăugăm query-ul în listă doar dacă q_text a fost populat
    if q_text:
        queries.append({
            "id": i,
            "query": q_text,
            "type": structura,
            "metadata": {
                "complexity": "high" if len(q_text.split()) > 3 else "medium"
            }
        })

# Salvăm în folderul data
output_path = 'data/eval_queries_large.json'
try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2)
    print(
        f"Succes! S-a generat fișierul '{output_path}' cu {len(queries)} query-uri.")
except FileNotFoundError:
    with open('eval_queries_large.json', 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2)
    print("Fișierul a fost salvat local (data/ nu a fost găsit).")
