<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/cover-dark.svg">
  <img src="docs/assets/cover-light.svg" alt="spar-x-skills : des skills Claude Code prêtes pour la production, avec les deux commandes d'installation" width="100%">
</picture>

<p align="center">
  <a href="https://github.com/spar-x-fr/spar-x-skills/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/spar-x-fr/spar-x-skills/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Licence MIT" src="https://img.shields.io/badge/licence-MIT-blue.svg">
  <img alt="Plugin Claude Code" src="https://img.shields.io/badge/Claude%20Code-plugin-D97757.svg">
  <img alt="Spar-x certifié Qualiopi" src="https://img.shields.io/badge/Spar--x-Qualiopi-0B7A4B.svg">
</p>

<p align="center">
  <a href="#installation"><b>Installer</b></a> ·
  <a href="#skills-incluses"><b>Skills</b></a> ·
  <a href="skills/rightsize/README.md"><b>Documentation rightsize</b></a> ·
  <a href="https://github.com/spar-x-fr/spar-x-skills/discussions"><b>Discussions</b></a> ·
  <a href="#se-former-avec-spar-x"><b>Se former</b></a>
</p>

**Des skills Claude Code prêtes pour la production, sélectionnées et maintenues par [Spar-x](https://www.spar-x.fr), organisme de formation IA certifié Qualiopi.**

## Pourquoi `rightsize`

Un agent de code mal piloté coûte cher de deux façons : il rend un travail approximatif, ou il dépense des tokens là où ça ne sert à rien (le plus gros modèle pour une simple recherche, toute la suite de tests pour une ligne modifiée, la même analyse faite deux fois).

`rightsize` règle les deux problèmes avec une règle simple : **la qualité d'abord, l'économie ensuite.**

- **Niveau expert sur le livrable** : causes racines trouvées, résultat vérifié, rien qu'un relecteur senior renverrait.
- **Le bon modèle pour chaque étape** : réflexion difficile une seule fois sur le modèle fort, exécution et vérifications mécaniques sur les modèles légers.
- **Des vérifications proportionnées** : on teste ce que le changement touche, pas tout le dépôt.
- **Des playbooks d'expert** par type de travail : bug, fonctionnalité, refactorisation, recherche, revue, migration, performance, documentation.

Résultat : des livrables du niveau des meilleurs, sans gaspiller le budget de l'équipe.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/proof-dark.svg">
  <img src="docs/assets/proof-light.svg" alt="100 exécutions valides notées par tests ou oracle ; coût d'Opus 5.5 en max 7,7 fois celui de high sans gain ; moins 98 pour cent sur une recherche routée, mêmes réussites" width="100%">
</picture>

Ces tâches sont bien spécifiées et vérifiables, et les échantillons sont petits : rien ici ne mesure le travail ouvert. [Détail et limites des mesures](skills/rightsize/README.md#measured-not-claimed).

## Skills incluses

| Skill | Ce qu'elle fait | Auteur |
|---|---|---|
| [`rightsize`](skills/rightsize/SKILL.md) | Qualité d'abord, puis le bon plan, le bon modèle (Haiku, Sonnet, Opus, Fable), le bon niveau d'effort et des vérifications proportionnées au changement. Montée en gamme sur preuve, jamais par habitude. | [Ayoub Hammoudi](https://github.com/Ayoubhm07)<br>Également maintenue par [Zakaria Khchiche](https://github.com/Zakariakhchiche) |

## Installation

Dans Claude Code :

```
/plugin marketplace add spar-x-fr/spar-x-skills
/plugin install spar-x-skills@spar-x-skills
```

Ou copiez le dossier `skills/rightsize/` dans `~/.claude/skills/`.

## Origine et modifications

`rightsize` vient du projet d'Ayoub Hammoudi ([LinkedIn](https://www.linkedin.com/in/ayoubhammoudi/)), sous licence MIT. Le dossier [`skills/rightsize/`](skills/rightsize/) contient le projet complet : la skill, ses scripts, les agents `rs-*`, les hooks, la documentation, les tests et le benchmark.

Différences avec l'original :

- les fichiers de la skill sont à la racine de `skills/rightsize/` et les chemins sont adaptés en conséquence ;
- la CI, les réglages du dépôt et le manifeste du plugin restent dans le dépôt d'origine ;
- ce plugin active uniquement la skill. Les agents `rs-*` et les hooks présents dans le dossier ne se chargent pas seuls : installez le plugin d'origine pour en profiter, ou suivez [l'installation manuelle](skills/rightsize/docs/getting-started.md#manual-install-without-the-plugin-system).

## Se former avec Spar-x

Cette skill applique ce que nous enseignons : piloter des agents IA pour qu'ils produisent un travail fiable et maîtrisé en coût.

- **IA agentique pour décideurs** : 1 jour, à distance. Prochaines sessions : décembre 2026, 11 février, 11 mars et 8 avril 2027.
- **Agents IA Microsoft** : Copilot Studio, Microsoft Foundry, Agent Framework.
- Organisme certifié Qualiopi : formations finançables par votre OPCO.

[Demander un devis](https://forms.gle/ARaTCq9ADgqvJfKL8) · [spar-x.fr](https://www.spar-x.fr)

## Communauté

- [Discussions](https://github.com/spar-x-fr/spar-x-skills/discussions) : questions, idées, retours d'expérience.
- [Contribuer](CONTRIBUTING.md) · [Obtenir de l'aide](SUPPORT.md) · [Code de conduite](CODE_OF_CONDUCT.md) · [Sécurité](SECURITY.md)

## Contact

- Site : [spar-x.fr](https://www.spar-x.fr)
- LinkedIn : [Spar-x](https://www.linkedin.com/company/105543518/)
- E-mail : formation@spar-x.fr
- Téléphone : 06 51 48 47 86
- Paris, France

## Mainteneurs

| Nom | GitHub | LinkedIn |
|---|---|---|
| Zakaria Khchiche | [@Zakariakhchiche](https://github.com/Zakariakhchiche) | [linkedin.com/in/zakariakhchiche](https://www.linkedin.com/in/zakariakhchiche/) |
| Ayoub Hammoudi | [@Ayoubhm07](https://github.com/Ayoubhm07) | [linkedin.com/in/ayoubhammoudi](https://www.linkedin.com/in/ayoubhammoudi/) |

## Licence

MIT, voir [LICENSE](LICENSE). Copyright d'origine : Ayoub Hammoudi.
