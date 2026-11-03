# Notes pour les mainteneurs

## Réglages appliqués sur GitHub

- Fusion par squash uniquement, suppression automatique des branches après fusion ;
  wiki et projets désactivés.
- Jeton des workflows en lecture seule par défaut ; les workflows ne peuvent pas
  approuver de pull request.
- Actions limitées à celles de GitHub et à une liste blanche
  (`step-security/harden-runner`, `trufflesecurity/trufflehog`, `ossf/scorecard-action`),
  SHA complet obligatoire.
- Graphe de dépendances, alertes Dependabot et correctifs de sécurité automatiques.
- Scan de secrets avec blocage des pushes, signalement privé des vulnérabilités.
- Ruleset `Protection de main`, versionné dans
  [`.github/rulesets/protect-main.json`](../.github/rulesets/protect-main.json) :
  pull request obligatoire, pas de suppression ni de force-push, historique linéaire,
  conversations résolues, checks obligatoires sur une branche à jour
  (`lint`, `format`, `types`, `tests (3.12)`, `zizmor`, `trufflehog`). Les autres
  versions de Python tournent dans la matrice sans être exigées.

Réappliquer le ruleset après une modification du fichier (remplacer `<id>` par
l'identifiant affiché dans *Settings → Rules*) :

```bash
gh api -X PUT repos/spar-x-fr/spar-x-skills/rulesets/<id> --input .github/rulesets/protect-main.json
```

## CI

| Workflow | Jobs |
|---|---|
| `ci.yml` | ruff (lint, format), mypy strict, tests unittest Python 3.9 à 3.13 |
| `security.yml` | zizmor (workflows et Dependabot), TruffleHog sur tout l'historique |
| `codeql.yml` | CodeQL Python et Actions (dépôt public uniquement) |
| `scorecard.yml` | OpenSSF Scorecard (dépôt public uniquement) |

Chaque workflow démarre avec `permissions: {}` ; chaque job déclare ses permissions,
utilise harden-runner, un checkout sans identifiants persistés et un `timeout-minutes`.
Pas de `pull_request_target`.

## Mettre à jour les épinglages

- Dependabot ouvre chaque semaine une PR groupée pour les actions et une pour les
  outils Python de `skills/rightsize/requirements-dev.txt` (délai de 7 jours après
  chaque publication).
- À la main : prendre le SHA du tag via l'API
  (`gh api repos/<owner>/<action>/git/ref/tags/<tag>`, puis l'objet pointé si le tag
  est annoté) et garder la version en commentaire : `uses: owner/action@<sha> # vX.Y.Z`.
- Pour les outils Python, prendre chaque hachage dans l'API JSON de PyPI et vérifier
  avec `pip install --require-hashes --no-deps -r requirements-dev.txt`. Une PR
  Dependabot qui échoue à l'installation signale souvent une nouvelle dépendance
  de l'outil, absente du fichier : l'ajouter avec ses hachages.
- La version de l'image TruffleHog (`version:` dans `security.yml`) se met à jour en
  même temps que le SHA de l'action.

## Reste à surveiller

- Un job « Queued » puis annulé sans étape exécutée n'est pas un échec de test :
  vérifier le runner et la case de la matrice.
