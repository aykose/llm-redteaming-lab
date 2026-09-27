import sys
import json
from stats import compute_stats


def charger(chemin):
    with open(chemin) as f:
        data = json.load(f)
    return data["meta"]["modele"], data["resultats"]


if len(sys.argv) < 3:
    print("Usage : python3 compare.py <rapport1.json> <rapport2.json>")
    sys.exit(1)

modele_a, resultats_a = charger(sys.argv[1])
modele_b, resultats_b = charger(sys.argv[2])

stats_a = compute_stats(resultats_a)
stats_b = compute_stats(resultats_b)

# ── Vue catégorie : taux de bypass judge côte à côte ──
print(f"\n=== COMPARAISON : {modele_a} vs {modele_b} ===\n")
print(f"{'Catégorie':<22} {modele_a:<15} {modele_b:<15}")
print("-" * 52)

categories = set(stats_a) | set(stats_b)
for cat in sorted(categories):
    a = stats_a[cat]
    b = stats_b[cat]
    col_a = f"{a['bypass_judge']}/{a['total']}"
    col_b = f"{b['bypass_judge']}/{b['total']}"
    print(f"{cat:<22} {col_a:<15} {col_b:<15}")

# ── Vue payload : divergences de verdict judge entre les deux ──
print(f"\n=== DIVERGENCES PAR PAYLOAD (judge) ===\n")

verdicts_a = {r["nom"]: r["judge"] for r in resultats_a}
verdicts_b = {r["nom"]: r["judge"] for r in resultats_b}

divergences = 0
for nom in verdicts_a:
    if nom in verdicts_b and verdicts_a[nom] != verdicts_b[nom]:
        print(f"{nom:<25} {modele_a}: {verdicts_a[nom]}  |  {modele_b}: {verdicts_b[nom]}")
        divergences += 1

if divergences == 0:
    print("Aucune divergence de verdict.")
else:
    print(f"\nTotal : {divergences} divergence(s)")
