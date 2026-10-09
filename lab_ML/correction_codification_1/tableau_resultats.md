# Correction de la codification 1 par machine learning : journal des résultats

> Essai **bonus et indépendant** des autres branches de machine learning du projet : il n'en reprend aucun choix (variables, encodages, transformations, réglages). Notebooks : [`01_ml_septembre.ipynb`](01_ml_septembre.ipynb) (machine learning de septembre, sur le niveau 0 tel quel), puis [`02_corrections_manuelles.ipynb`](02_corrections_manuelles.ipynb) (codifications 1 d'avril à août, correctif appliqué après le machine learning s'il est concluant ; leurs 28 clients ont tous `PAY_1` = 1, ils ne sont ni dans le train ni dans le test). Les passages 1 à 5 ont été faits dans un premier notebook unique, `correction_codification1.ipynb`, scindé ensuite en ces deux notebooks.

## 1. Cadre

- **Hypothèse testée, une seule** : la codification 1 est un **code d'attente**, posé par la banque à la place d'une vraie codification qu'elle n'a pas encore tranchée. Si un modèle sait dire ce que cache un 1, l'hypothèse tient ; s'il ne sait pas décider, le 1 est autre chose.
- **Données** : niveau 0 du nettoyage (`data/creditcard_pret_ingestion.csv`, 30 000 clients), sans `dpnm` (jamais utilisé), sans `ID` ; aucune colonne ajoutée.
- **Codifications 1 d'avril à août** (34 valeurs, 28 clients) : leurs 28 clients ont tous `PAY_1` = 1, hors du train et du test ; tranchées en correctif, à appliquer après le machine learning s'il est concluant, à la main (7 clients) et par une règle (21 clients : si `PAY_3` <= 0 et `BILL_AMT2` <= 0, alors `PAY_2` = `PAY_3`, plus d'encours fin août). Décisions et raisons : section 3 de `02_corrections_manuelles`.
- **Septembre** : cible `PAY_1`, codifications détaillées (-2 à 8) ; les 3 688 `PAY_1` = 1 sont mis de côté. Découpage 80/20 train / test (`stratify` sur `PAY_1`, `random_state=42`), puis 80/20 train / validation dans le train ; le test n'est pas encore lu.
- **Mesure** : part des clients rangés dans la bonne **famille** (-2, -1, 0, 2 et plus), en validation, globale et par famille.
- **Points de comparaison** : « même codification qu'en août » (`PAY_1` = `PAY_2`), règle naïve à battre ; « toujours 0 », plancher.
- **Critères fixés avant la lecture du test** : A, le modèle fait nettement mieux que la règle naïve sur le test ; B, sur les `PAY_1` = 1, il tranche aussi nettement que sur le test.

## 2. Premiers passages (paramètres standards, validation)

Points de comparaison, identiques dans tous les passages (validation, 4 210 clients) :

| | Global | -2 | -1 | 0 | 2 et plus |
|---|---|---|---|---|---|
| Même codification qu'en août | 89,9 % | 91,6 % | 83,1 % | 97,1 % | 66,5 % |
| Toujours 0 | 56,0 % | 0 % | 0 % | 100 % | 0 % |

| Passage | Ce qui change | Modèle | Global | -2 | -1 | 0 | 2 et plus | Décision |
|---|---|---|---|---|---|---|---|---|
| 1 | Variables : `PAY_2` à `PAY_6`, montants, plafond, **ratios de paiement ajoutés** ; montants au logarithme signé (`arcsinh`) pour la régression logistique et le MLP ; `PAY_n` en catégories pour la régression logistique et le MLP, en nombres pour les arbres | Régression logistique | 91,1 % | 93,7 % | 88,1 % | 97,4 % | 65,1 % | **Écarté** : ratios et `arcsinh` repris d'autres branches, sans validation |
| | | MLP | 91,0 % | 94,6 % | 87,9 % | 96,9 % | 66,1 % | |
| | | RandomForest | 91,7 % | 94,1 % | 90,5 % | 97,3 % | 65,1 % | |
| | | CatBoost | 91,8 % | 94,3 % | 90,4 % | 97,5 % | 65,1 % | |
| 2 | `PAY_n` en catégories pour les arbres aussi (une colonne par valeur pour RandomForest, `cat_features` pour CatBoost) | RandomForest | 91,6 % | 93,7 % | 90,7 % | 97,4 % | 64,1 % | Écarts d'un point au plus (bruit) ; catégories gardées : l'ordre entre -2, -1 et 0 n'est pas documenté. CatBoost passe de 10 à 62 s |
| | | CatBoost | 91,8 % | 94,3 % | 90,5 % | 97,5 % | 65,1 % | |
| 3 | Arbre de décision ajouté (profondeur 5) | Arbre de décision | 91,4 % | 94,1 % | 90,2 % | 97,0 % | 64,7 % | Écarté avec le passage 1 (ratios) |
| 4 | Toutes les colonnes d'origine sauf `ID` et `dpnm` (données personnelles comprises), **sans ratios ni `arcsinh`** ; mise à l'échelle standard des nombres | Régression logistique | 90,8 % | 91,6 % | 88,0 % | 97,3 % | 64,9 % | Données personnelles retirées pour le passage 5 : non pertinentes pour une codification |
| | | MLP | 89,9 % | 92,3 % | 85,6 % | 96,2 % | 65,9 % | |
| | | Arbre de décision | 90,9 % | 94,1 % | 90,9 % | 96,9 % | 60,1 % | |
| | | RandomForest | 91,4 % | 93,0 % | 90,4 % | 97,3 % | 64,1 % | |
| | | CatBoost | 91,7 % | 93,9 % | 89,8 % | 97,6 % | 65,3 % | |
| 5 | Sans les données personnelles (`SEX`, `EDUCATION`, `MARRIAGE`, `AGE`) ; tableau des clients qui changent de famille entre août et septembre ajouté | Régression logistique | 91,0 % | 91,6 % | 88,5 % | 97,4 % | 64,9 % | **Retenu** : sans les données personnelles, écarts d'un point au plus avec le passage 4 (bruit), MLP +0,9 point et moins de surapprentissage |
| | | MLP | 90,8 % | 91,6 % | 88,1 % | 97,1 % | 65,1 % | |
| | | Arbre de décision | 90,9 % | 94,1 % | 90,9 % | 96,9 % | 59,9 % | |
| | | RandomForest | 91,6 % | 94,3 % | 90,4 % | 97,4 % | 64,3 % | |
| | | CatBoost | 91,7 % | 94,1 % | 89,9 % | 97,6 % | 64,7 % | |

Bonnes prédictions sur le train au passage 4 : régression logistique 90,5 %, MLP 93,3 %, arbre de décision 90,5 %, RandomForest 100 %, CatBoost 93,1 %. Au passage 5 : régression logistique 90,5 %, MLP 92,5 %, arbre de décision 90,5 %, RandomForest 100 %, CatBoost 93,4 %.

**Clients qui changent de famille entre août et septembre** (passage 5, validation ; la règle naïve en retrouve 0 % par construction) :

| Type de changement | Clients | Régression logistique | MLP | Arbre de décision | RandomForest | CatBoost |
|---|---|---|---|---|---|---|
| Sortie du retard (2 et plus en août, sain en septembre) | 78 | 65,4 % | 73,1 % | 83,3 % | 80,8 % | 80,8 % |
| Nouveau retard (sain en août, 2 et plus en septembre) | 168 | 0 % | 0 % | 0 % | 0 % | 0 % |
| Changement entre codifications saines | 181 | 4,4 % | 16,0 % | 9,9 % | 16,0 % | 22,1 % |
| Tous les clients qui changent | 427 | 13,8 % | 20,1 % | 19,4 % | 21,5 % | 24,1 % |

## 3. Constats

- **Passages 1 à 4** : les modèles battent la règle naïve de 1 à 2 points au global, surtout sur la famille -1 (jusqu'à +7 points) et sur -2 (+2 à 3 points) ; **aucun ne fait mieux qu'elle sur la famille 2 et plus**.
- **Passage 3** : l'arbre de décision à 5 niveaux fait presque aussi bien que CatBoost (91,4 % contre 91,8 %) ; ses règles commencent par la codification d'août, puis par la part de la facture payée.
- **Passage 4** : le MLP surapprend (93,3 % en train, 89,9 % en validation) ; réglage à faire si le tableau des clients qui changent de famille montre que les modèles en retrouvent une part réelle.
- **Passage 5, données personnelles** : les retirer ne fait rien perdre (écarts d'un point au plus avec le passage 4).
- **Passage 5, clients qui changent de famille** : les modèles à base d'arbres retrouvent **8 sorties du retard sur 10** (78 clients en validation) ; **aucun nouveau retard** n'est retrouvé, par aucun modèle (168 clients) ; les changements entre codifications saines le sont peu (4 à 22 %). La part de retards maintenus que les modèles classent à tort en sortie n'est pas encore mesurée : la famille 2 et plus reste un peu sous la règle naïve (59,9 à 65,1 % contre 66,5 %).
