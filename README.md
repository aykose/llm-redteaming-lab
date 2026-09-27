# LLM Red-Teaming Lab — Évaluation de robustesse aux attaques par prompt

Outil d'évaluation automatisée de la robustesse d'un LLM face à des attaques
par prompt injection et jailbreak. Le lab envoie un corpus de payloads classés
par famille d'attaque à un modèle cible (servi localement via Ollama), collecte
ses réponses, et évalue si les garde-fous ont été contournés à l'aide de deux
détecteurs indépendants. Les résultats sont horodatés et comparables entre
modèles.

> Projet à visée pédagogique et défensive : il mesure et caractérise la
> robustesse d'un modèle, il ne cherche pas à produire de nouvelles attaques.
> Le corpus est constitué de techniques de jailbreak publiques et connues, avec
> des cibles volontairement génériques et des témoins bénins (canaris).

## Fonctionnalités

- **Cible locale paramétrable** : le modèle attaqué est passé en argument, servi
  par Ollama. Aucun appel à une API cloud, aucun quota, tests illimités.
- **Corpus classé par famille d'attaque** : instruction override, roleplay,
  output priming, framing hypothétique, obfuscation, prompt leak, social
  engineering, plus des canaris bénins de contrôle.
- **Double détection** :
  - *keyword* — détection de marqueurs de refus (rapide, mais sujette aux faux
    positifs/négatifs) ;
  - *LLM-as-a-judge* — un modèle juge évalue sémantiquement si la réponse a cédé.
- **Juge fixe** : le modèle juge reste constant pendant que la cible varie, pour
  isoler l'effet de la cible dans les comparaisons.
- **Rapports horodatés** : chaque run produit un JSON avec les réponses, les deux
  verdicts, un timestamp par test, et des métadonnées (modèle, durée du run,
  nombre de payloads).
- **Comparaison multi-modèles** : `compare.py` met deux rapports côte à côte,
  taux de bypass par catégorie et divergences de verdict par payload.

## Architecture

| Fichier            | Responsabilité                                              |
|--------------------|-------------------------------------------------------------|
| `main.py`          | Orchestration : lance la campagne sur un modèle, écrit le rapport |
| `target.py`        | `send_prompt` — envoie un prompt au modèle via l'API Ollama |
| `detector.py`      | `is_attack_successful` — détection par mots-clés + appel au juge |
| `judge.py`         | `judge_response` — évaluation LLM-as-a-judge                 |
| `rkeyword.py`      | Liste des marqueurs de refus                                 |
| `payloads_data.py` | Corpus de payloads classés par `type`                       |
| `stats.py`         | `compute_stats` / `print_stats` — agrégation par catégorie   |
| `compare.py`       | Comparaison de deux rapports                                 |

Le modèle cible circule en argument de `send_prompt`. Le juge utilise un modèle
fixe (valeur par défaut de `send_prompt`), pour rester constant d'un run à l'autre.

## Prérequis

- [Ollama](https://ollama.com/) installé et en service
- Python 3.10+
- Les modèles à tester, par exemple :

```bash
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

Lancer une campagne sur un modèle cible :

```bash
cd src && python3 main.py llama3.2:3b
```

Le script vérifie que le modèle est bien installé dans Ollama avant de lancer,
exécute le corpus, affiche un récapitulatif par catégorie et écrit un rapport
horodaté dans `rapport/`.

Comparer deux rapports :

```bash
cd src && python3 compare.py rapport/run_AAAAMMJJ_HHMMSS.json rapport/run_AAAAMMJJ_HHMMSS.json
```

## Interprétation des résultats

Chaque test est évalué par deux détecteurs, `keyword` et `judge`, dont les
verdicts peuvent diverger. Ces divergences sont le cœur de l'analyse :

- **faux positif keyword** : une réponse bénigne sans marqueur de refus est
  comptée comme un bypass (visible sur les canaris) ;
- **faux négatif judge** : une réponse qui fournit le contenu nuisible enrobé
  d'avertissements ("à des fins éducatives", "voici ce qu'il faut éviter") peut
  être classée à tort comme un refus.

**La validation manuelle d'un échantillon reste nécessaire** : les verdicts
automatiques donnent une borne, pas une vérité. Un taux de bypass automatique est
à lire comme un plancher.

## Limites connues

- Le modèle juge est un modèle local de taille modeste : il produit des faux
  négatifs sur les réponses hybrides (contenu + disclaimer) et gagnerait à être
  remplacé par un juge plus capable.
- Le corpus couvre les techniques publiques mono-tour ; il ne couvre pas les
  attaques multi-tours ni les payloads adaptatifs.
- L'absence de bypass détecté ne prouve pas la sûreté du modèle : elle documente
  une résistance sur un périmètre défini.

## Pistes d'évolution

- Renforcer le prompt du juge pour rattraper les réponses hybrides
- Élargir le corpus (familles et variantes)
- Ajouter un taux de désaccord keyword/judge au récapitulatif
- Étendre la comparaison à N modèles
