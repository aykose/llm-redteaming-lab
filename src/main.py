import json
import os
import time
import sys
import requests
from datetime import datetime
from detector import is_attack_successful
from target import send_prompt
from payloads_data import payloads
from stats import compute_stats, print_stats


if len(sys.argv) < 2:
    print("Usage : python3 main.py <nom_du_model>")
    print("Exemple : python3 main.py llama3.2:1b")
    sys.exit(1)

model = sys.argv[1]

data = requests.get("http://localhost:11434/api/tags").json()
noms = [m["name"] for m in data["models"]]

if len(sys.argv) < 2 or sys.argv[1] not in noms:
    print(f"Modeles disponibles : {noms}")
    print("Usage : python3 main.py <nom_du_model>")
    print("Exemple : python3 main.py llama3.2:1b")
    sys.exit(1)


results = []

debut = time.perf_counter()

for i in payloads:
    response = send_prompt(i["prompt"], model)
    bool1, bool2 = is_attack_successful(response)
    results.append({
        "nom": i["nom"],
        "type" : i["type"],
        "prompt": i["prompt"],
        "response": response,
        "keyword": bool1,
        "judge": bool2,
        "timestamp": datetime.now().isoformat()
    })

duree = time.perf_counter() - debut


rapport = {
    "meta": {
        "duree_secondes": duree,
        "modele": model,
        "nb_payloads": len(payloads),
        "date": datetime.now().isoformat()
    },
    "resultats": results
}

os.makedirs("rapport", exist_ok=True)

nom_fichier = f"rapport/run_{datetime.now():%Y%m%d_%H%M%S}.json"
with open(nom_fichier, "w") as f:
    json.dump(rapport, f, indent=2, ensure_ascii=False)


print(f"Rapport écrit : {nom_fichier}")
stats = compute_stats(results)
print_stats(stats)

