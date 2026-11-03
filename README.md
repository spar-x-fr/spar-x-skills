# spar-x-skills

**Des skills Claude Code prêtes pour la production, sélectionnées et maintenues par [Spar-x](https://www.spar-x.fr), organisme de formation IA certifié Qualiopi.**

## Pourquoi `rightsize`

Un agent de code mal piloté coûte cher de deux façons : il rend un travail approximatif, ou il dépense des tokens là où ça ne sert à rien (le plus gros modèle pour une simple recherche, toute la suite de tests pour une ligne modifiée, la même analyse faite deux fois).

`rightsize` règle les deux problèmes avec une règle simple : **la qualité d'abord, l'économie ensuite.**

- **Niveau expert sur le livrable** : causes racines trouvées, résultat vérifié, rien qu'un relecteur senior renverrait.
- **Le bon modèle pour chaque étape** : réflexion difficile une seule fois sur le modèle fort, exécution et vérifications mécaniques sur les modèles légers.
- **Des vérifications proportionnées** : on teste ce que le changement touche, pas tout le dépôt.
- **Des playbooks d'expert** par type de travail : bug, fonctionnalité, refactorisation, recherche, revue, migration, performance, documentation.

Résultat : des livrables du niveau des meilleurs, sans gaspiller le budget de l'équipe.

## Skills incluses

| Skill | Ce qu'elle fait | Auteur |
|---|---|---|
| [`rightsize`](skills/rightsize/SKILL.md) | Qualité d'abord, puis le bon plan, le bon modèle (Haiku, Sonnet, Opus, Fable), le bon niveau d'effort et des vérifications proportionnées au changement. Montée en gamme sur preuve, jamais par habitude. | [Ayoub](https://github.com/Ayoubhm07) |

## Installation

Dans Claude Code :

```
/plugin marketplace add spar-x-fr/spar-x-skills
/plugin install spar-x-skills@spar-x-skills
```

Ou copiez le dossier `skills/rightsize/` dans `~/.claude/skills/`.

## Origine et modifications

`rightsize` vient du projet d'Ayoub, [Ayoubhm07/rightsize](https://github.com/Ayoubhm07/rightsize), sous licence MIT. Le dossier [`skills/rightsize/`](skills/rightsize/) contient le projet complet : la skill, ses scripts, les agents `rs-*`, les hooks, la documentation, les tests et le benchmark.

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

MIT, voir [LICENSE](LICENSE). Copyright d'origine : Ayoub.
