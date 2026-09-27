from collections import defaultdict


def compute_stats(results):
    stats = defaultdict(lambda: {"total": 0, "bypass_keyword": 0, "bypass_judge": 0})
    for r in results:
        stats[r["type"]]["total"] += 1
        if r["keyword"]:
            stats[r["type"]]["bypass_keyword"] += 1
        if r["judge"]:
            stats[r["type"]]["bypass_judge"] += 1
    return stats


def print_stats(stats):
    for categorie, compteurs in stats.items():
        total = compteurs["total"]
        kw = compteurs["bypass_keyword"]
        judge = compteurs["bypass_judge"]
        print(f"{categorie} : {judge}/{total} bypass (judge), {kw}/{total} (keyword)")
