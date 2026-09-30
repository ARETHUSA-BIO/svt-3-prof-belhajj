# Vérification pédagogique et didactique — SVT 3

## Périmètre

Le quiz vise la révision de notions de SVT destinées à la **3e année Sciences expérimentales en Tunisie**. La pièce jointe annonçait 3 thèmes × 60 questions, mais son contenu s’interrompt à la question 48 du thème « Information génétique » et ne contient aucune question du thème « Dynamique du globe terrestre et évolution biologique ».

| Thème | Questions fournies | Compléments ajoutés | Total dans l’application |
|---|---:|---:|---:|
| Nutrition et santé | 60 | 0 | 60 |
| Information génétique | 48 | 12 | 60 |
| Dynamique du globe terrestre et évolution biologique | 0 | 60 | 60 |
| **Total** | **108** | **72** | **180** |

Chaque question possède une réponse indexée, une explication et un type explicite (`qcm` ou `vrai-faux`). Les questions issues de la pièce jointe sont marquées `origine: fourni`; les questions rédigées pour compléter les sections manquantes sont marquées `origine: complément`.

## Vérifications et précisions effectuées

- Les 72 questions de complément couvrent les bases ADN/hérédité/méiose puis structure terrestre, tectonique, séismes, volcanisme, fossiles, indices de parenté et mécanismes évolutifs.
- Les questions QCM à réponses multiples indiquent clairement qu’il peut y avoir plusieurs choix corrects.
- Les définitions fournies sans choix ni clé ont été intégrées en questions Vrai/Faux, en conservant leur formulation comme proposition vérifiable.
- **Nutrition, question 3** : la clé fournie incluait l’hydrolysabilité d’un acide aminé. La clé a été restreinte à l’incorporation des acides aminés dans les protéines, avec une explication rappelant que l’hydrolyse d’une protéine libère des acides aminés.
- **Nutrition, question 8** : la proposition « acides aminés » a été précisée en « certains acides aminés aromatiques », car le test xanthoprotéique ne caractérise pas indistinctement tous les acides aminés.
- **Génétique, question 7** : la clé fournie attribuait l’albinisme à l’absence de mélanocytes. La correction retient l’hérédité et la diminution/absence de mélanine ; les mélanocytes sont généralement présents.
- **Génétique, question 48** : la phrase sur deux parents « porteurs » a été reformulée : dans le modèle autosomal récessif classique, une personne atteinte a généralement hérité d’un allèle altéré de chacun de ses parents. Un parent atteint n’est pas nécessairement un « porteur non atteint ».
- Les contenus sur la santé (diabète, nutrition, carences et maladies) sont des éléments de cours et ne constituent pas des conseils médicaux personnalisés.

## Limites et recommandation de relecture

Cette vérification a contrôlé les structures, les clés, les explications et les notions générales ; elle ne constitue **ni une certification du ministère tunisien ni une validation exhaustive par l’enseignant du cours**. Le document source comporte des raccourcis pédagogiques ou des formulations discutables (par exemple, « préviennent contre l’infarctus », « préserve de façon spectaculaire », les seuils de glycémie et l’appellation « non insulinodépendant »). Ils sont conservés dans les questions provenant du document lorsqu’ils ne rendent pas la clé inexploitable ; il est recommandé à Prof. Belhajj de les confronter aux supports et au programme utilisés en classe avant une évaluation officielle.

Le périmètre Globe/Évolution a été composé pour compléter la démonstration, sans prétendre reproduire un référentiel officiel ligne par ligne. Les compléments et les ajustements de clé restent visibles dans `questions.json` afin de faciliter leur relecture ou leur remplacement.

## Contrôle automatisé

Le script de génération puis `npm test` vérifient : 180 questions au total, 60 par thème, options et explications présentes, indices de réponses valides, provenance, et présence de chaque illustration référencée dans le projet. Ces contrôles garantissent la cohérence des données, pas à eux seuls la justesse scientifique de chaque proposition.
