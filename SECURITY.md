# Politique de sécurité

## Signaler une vulnérabilité

Signalez-la en privé via les
**[avis de sécurité GitHub](https://github.com/spar-x-fr/spar-x-skills/security/advisories/new)**.
N'ouvrez pas de ticket public. Indiquez ce que vous avez trouvé, comment le reproduire
et l'impact attendu. Réponse sous 7 jours.

## Périmètre

Toutes les skills de ce dépôt, y compris leurs hooks et scripts : ils s'exécutent sur
la machine de l'utilisateur. Le détail propre à rightsize est dans
[skills/rightsize/SECURITY.md](skills/rightsize/SECURITY.md).

## Comment le dépôt se protège

- Branche `main` protégée : pull request, historique linéaire, checks obligatoires.
- Actions de CI épinglées par SHA complet, permissions minimales, outils de
  développement figés par version et hachage.
- Scan de secrets sur tout l'historique (TruffleHog), audit des workflows (zizmor),
  CodeQL et OpenSSF Scorecard.
