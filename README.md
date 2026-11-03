# spar-x-skills

Skills Claude Code sélectionnées par [Spar-x](https://www.spar-x.fr), organisme de formation IA.

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

`rightsize` vient du projet d'Ayoub, [Ayoubhm07/rightsize](https://github.com/Ayoubhm07/rightsize), sous licence MIT. Cette version reprend le fichier `SKILL.md` avec ses annexes (playbooks experts et référence de routage).

Différences avec l'original :

- les montants en dollars de l'annexe B sont écrits « USD 0.12 » au lieu de « $0.12 » : dans une skill, `$0`, `$1`… sont remplacés par les arguments de l'appel, ce qui rendait ces montants illisibles ;
- les scripts (`test_scope.py`, `token_audit.py`, `agent_audit.py`), les agents `rs-*` et les hooks ne sont pas inclus : installez le plugin d'origine pour en profiter. La skill indique déjà quoi faire sans eux.

## Mainteneurs

| Nom | GitHub | LinkedIn |
|---|---|---|
| Zakaria Khchiche | [@Zakariakhchiche](https://github.com/Zakariakhchiche) | [linkedin.com/in/zakariakhchiche](https://www.linkedin.com/in/zakariakhchiche/) |
| Ayoub Hammoudi | [@Ayoubhm07](https://github.com/Ayoubhm07) | [linkedin.com/in/ayoubhammoudi](https://www.linkedin.com/in/ayoubhammoudi/) |

## Licence

MIT, voir [LICENSE](LICENSE). Copyright d'origine : Ayoub.
