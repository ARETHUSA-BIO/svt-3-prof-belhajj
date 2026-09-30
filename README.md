# SVT 3 — Prof. Belhajj

Quiz web interactif en français pour les élèves de **3e année Sciences expérimentales — Tunisie**. L’application regroupe 180 questions réparties sur trois thèmes, avec réponses, explications, suivi local et fonctionnement hors ligne après le premier chargement.

## Démarrer en local

Aucune dépendance externe n’est nécessaire (Node.js 18+ suffit).

```bash
npm test
npm run build
npm run dev
```

Puis ouvrir `http://localhost:4173`. Le service local écoute sur le port `4173` par défaut ; `PORT=3000 npm run dev` permet de le changer. Pour une prévisualisation de la version produite, lancer `npm run build`, puis servir le dossier `dist/` avec un serveur HTTP statique. N’ouvrez pas `index.html` en `file://` : le chargement JSON et le service worker exigent une origine HTTP(S).

## Fonctionnalités

- Révision des 60 questions d’un thème, examen complet de 180 questions, ou quiz rapide de 15 questions.
- Ordre des questions et des choix mélangé à chaque partie.
- QCM à réponse unique ou multiple, et Vrai/Faux ; correction immédiate avec explication.
- Bilan avec score, pourcentage, temps, résultat par thème et erreurs à revoir.
- Reprise d’une séance interrompue, meilleure progression enregistrée localement, badges et thème clair/sombre.
- Interface responsive, navigation au clavier, états annoncés aux technologies d’assistance et respect de `prefers-reduced-motion`.
- PWA : les fichiers de l’application, les 180 questions et les illustrations sont mis en cache sur l’appareil ; un chargement initial réussi est nécessaire pour l’utilisation hors ligne.

## Données, provenance et corrections

Les questions sont dans [`questions.json`](questions.json), séparées du code d’interface. Le fichier source reçu, conservé dans `content/source-brief.txt`, contenait **60 questions de Nutrition** et **48 questions de Génétique**, mais aucune question du thème Globe/Évolution. Il manquait donc 72 questions pour atteindre les 180 demandées : **12 compléments de Génétique (49–60)** et **60 compléments Globe/Évolution** ont été rédigés et portent `"origine": "complément"`. Les questions reprises du document portent `"origine": "fourni"`.

Le script [`scripts/generate_bank.py`](scripts/generate_bank.py) reconstruit la banque à partir du document conservé et ajoute les 72 compléments. Il précise quelques formulations ou clés de correction pour éviter des raccourcis scientifiques ; ces révisions sont signalées par `note_pedagogique`. Pour modifier une question, éditer le script puis régénérer `questions.json`, ou éditer directement le JSON (dans ce cas, ne pas exécuter le script de génération ensuite sans répercuter la modification dans le script).

Schéma simplifié d’une question :

```json
{
  "id": 1,
  "type": "qcm",
  "question": "Énoncé…",
  "options": ["Choix A", "Choix B"],
  "reponses_correctes": [0],
  "explication": "Pourquoi cette réponse est juste…",
  "origine": "fourni",
  "theme": "nutrition"
}
```

Pour un Vrai/Faux, conserver `"type": "vrai-faux"`, les options `[`"Vrai"`, `"Faux"`]` et l’index correct. Les index commencent à zéro. Les illustrations facultatives utilisent le champ `illustration` (`src`, `alt`, `credit`) et doivent rester dans `assets/` pour être disponibles hors ligne.

## Illustrations et licences

Les images utilisées par l’interface sont copiées dans `assets/` ; l’application ne sollicite aucun domaine d’image externe.

- **Système digestif** — Mariana Ruiz (LadyofHats), domaine public mondial, [page Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Digestive_system_diagram_en.svg).
- **Double hélice de l’ADN** — Genomics Education Programme, [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/), [page Wikimedia Commons](https://commons.wikimedia.org/wiki/File:DNA_double_helix_(13081113544).jpg). Crédit conservé dans les métadonnées de l’illustration dans `questions.json`.
- **Limites des plaques tectoniques** — Jose F. Vigil / USGS, domaine public des États-Unis, [page Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Tectonic_plate_boundaries.png).

Aucune image n’est un lien cliquable dans l’application. Les crédits et liens de licence ci-dessus sont fournis dans cette documentation.

## Vie privée et sécurité

Pas de compte, nom, e-mail, chat, publicité, traceur ou cookie tiers. Les réponses de la séance, le meilleur score et le choix d’affichage ne quittent pas le navigateur et peuvent être supprimés en effaçant les données de ce site dans les paramètres du navigateur. Il n’y a pas de base de données ni de serveur applicatif. Les contenus restent dans l’application ; les attributions externes ci-dessus ne sont pas affichées comme liens de navigation dans l’interface du quiz.

## Vérifications

```bash
npm test
npm run build
```

Les tests contrôlent le nombre de questions, le format, les index de réponses, les explications, la provenance, la présence des illustrations locales et l’absence de scripts de suivi tiers.
