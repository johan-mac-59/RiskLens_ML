# Correction de la codification 1 par machine learning : journal des résultats

> Essai **bonus et indépendant** des autres branches de machine learning du projet : il n'en reprend aucun choix (variables, encodages, transformations, réglages). Notebooks : [`01_ml_septembre.ipynb`](01_ml_septembre.ipynb) (machine learning de septembre, sur le niveau 0 tel quel), puis ses variantes [`01b_ml_septembre_log.ipynb`](01b_ml_septembre_log.ipynb) (montants et plafond au logarithme), [`01c_optimisation.ipynb`](01c_optimisation.ipynb) (boucle d'optimisation), [`01d_optimisation_cible_regroupee.ipynb`](01d_optimisation_cible_regroupee.ipynb) (cible regroupée), [`01e_optimisation_tout_regroupe.ipynb`](01e_optimisation_tout_regroupe.ipynb) (cible et variables regroupées) et [`01f_optimisation_mois_empiles.ipynb`](01f_optimisation_mois_empiles.ipynb) (apprentissage sur les mois d'avril à septembre empilés), puis [`02_corrections_manuelles.ipynb`](02_corrections_manuelles.ipynb) (codifications 1 d'avril à août, correctif appliqué après le machine learning s'il est concluant ; leurs 28 clients ont tous `PAY_1` = 1, ils ne sont ni dans le train ni dans le test). Les passages 1 à 5 ont été faits dans un premier notebook unique, `correction_codification1.ipynb`, scindé ensuite en ces deux notebooks.

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
- **Passage 6** (`01_ml_septembre`, mêmes réglages que le passage 5, scores identiques ; tableaux ajoutés) :
  - **niveaux de retard d'août à septembre (train)** : 1 808 clients à 2 en août : 1 266 restent à 2, 216 passent à 3, 326 sortent ; les retards de 3 et plus montent d'un cran, restent au même niveau ou redescendent à 2 (57 clients de 3 à 2, 11 de 4 à 2) ; 7 en août donne toujours 8 (15 clients) ; les 799 nouveaux retards de septembre sont tous posés à 2 ;
  - **retards maintenus (validation, 333 clients)** : retrouvés à 97 ou 98 % par la régression logistique, le MLP, RandomForest et CatBoost (90,1 % pour l'arbre de décision) : trouver des sorties du retard ne coûte que 2 à 3 % des retards maintenus ;
  - **codification 2 attribuée (validation, 427 vraies)** : CatBoost en attribue 301, dont 245 justes (81 %) ; la règle naïve 359, dont 246 justes (69 %) ; les retards manqués sont surtout les 168 nouveaux retards, qu'aucun modèle ne retrouve ;
  - **codifications 3 et plus** : attribuées par tous les modèles sauf l'arbre de décision, rarement justes pour 3 (CatBoost 8 sur 24 attribuées, 52 vraies), justes pour 6 à 8 (quelques clients chacune).
- **Passage 7** (`01b_ml_septembre_log`, variante du passage 6 : montants dus, payés et plafond au logarithme signé, puis standardisés pour la régression logistique et le MLP ; validation) :

| Modèle | Global | -2 | -1 | 0 | 2 et plus | Sorties du retard (78) | Retards maintenus (333) | Nouveaux retards (168) | Changements entre sains (181) | Tous les changements (427) |
|---|---|---|---|---|---|---|---|---|---|---|
| Régression logistique | 91,0 % (=) | 93,2 % (+1,6) | 87,7 % (-0,8) | 97,5 % | 64,9 % (=) | 67,9 % (+2,5) | 97,6 % (=) | 0 % | 9,9 % (+5,5) | 16,6 % (+2,8) |
| MLP | 91,0 % (+0,2) | 94,6 % (+3,0) | 87,5 % (-0,6) | 97,0 % | 65,7 % (+0,6) | 76,9 % (+3,8) | 97,0 % (-0,9) | 3,6 % (+3,6) | 24,3 % (+8,3) | **25,8 %** (+5,7) |
| Arbre de décision | 90,9 % (=) | 94,1 % | 90,9 % | 96,9 % | 59,9 % | 83,3 % | 90,1 % | 0 % | 9,9 % | 19,4 % (=) |
| RandomForest | 91,7 % (+0,1) | 94,3 % | 90,8 % | 97,4 % | 64,3 % | 80,8 % | 96,7 % | 0 % | 18,2 % (+2,2) | 22,5 % (+1,0) |
| CatBoost | 91,7 % (=) | 94,1 % | 89,9 % | 97,6 % | 64,7 % | 80,8 % | 97,3 % | 0 % | 22,1 % | 24,1 % (=) |

  Entre parenthèses : écart avec le passage 6, en points. Bonnes prédictions sur le train : régression logistique 90,8 %, MLP 93,1 %, arbre de décision 90,5 %, RandomForest 100 %, CatBoost 93,4 %.
  - **Arbres** : résultats identiques ou presque, comme attendu (le logarithme ne change pas l'ordre des montants).
  - **Régression logistique et MLP** : même score global, mais davantage de changements retrouvés (MLP +5,7 points, environ 24 clients sur 427, au niveau de CatBoost) ; le MLP retrouve ses premiers nouveaux retards (6 sur 168).
  - **Nouveaux retards** : toujours pas retrouvés (3,6 % au mieux).
- **Passage 8** (`01c_optimisation` : boucle d'optimisation, validation croisée à 5 plis sur le train, score optimisé = moyenne des quatre familles, surapprentissage limité à 7 % relatif ; montants et plafond au logarithme signé) :

| Modèle | Réglage retenu | Validation (moyenne des 4 familles) | Train | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|
| Régression logistique | C = 10, classes équilibrées | 86,05 % ± 0,65 | 86,23 % | 0,22 % | 21 s |
| Arbre de décision | entropy, profondeur 5, feuilles 1, sans poids | 85,88 % ± 0,62 | 86,08 % | 0,23 % | 2 s |
| RandomForest | 100 arbres, profondeur 20, feuilles 2, `max_features` 0,5, `balanced_subsample` | 86,84 % ± 0,58 | 92,69 % | 6,31 % | 327 s |
| MLP | couches (256, 128), alpha 10⁻⁶ | 86,51 % ± 0,49 | 87,31 % | 0,92 % | 36 s |
| CatBoost | profondeur 5, `learning_rate` 0,1, `l2_leaf_reg` 5, `Balanced` | 87,01 % ± 0,63 | 89,77 % | 3,08 % | 1 164 s |

  Aucune alerte de variance (écart-type des plis de 0,49 à 0,65 point). Prédictions hors pli sur le train (21 049 clients) :

| Modèle | Bonnes prédictions | -2 | -1 | 0 | 2 et plus | Sorties du retard (366) | Retards maintenus (1 705) | Nouveaux retards (799) | Changements entre sains (998) |
|---|---|---|---|---|---|---|---|---|---|
| Régression logistique | 89,0 % | 94,9 % | 84,7 % | 93,3 % | 71,2 % | 38,3 % | 98,7 % | 12,6 % | 9,4 % |
| Arbre de décision | 90,5 % | 95,0 % | 86,9 % | 96,4 % | 65,3 % | 52,2 % | 95,8 % | 0 % | 9,9 % |
| RandomForest | 91,1 % | 95,1 % | 88,4 % | 96,4 % | 67,4 % | 74,6 % | 98,1 % | 2,0 % | 12,2 % |
| MLP | 91,1 % | 95,1 % | 87,6 % | 96,9 % | 66,4 % | 77,3 % | 97,3 % | 0,5 % | 20,1 % |
| CatBoost | 89,6 % | 94,9 % | 89,2 % | 92,7 % | 71,3 % | 68,9 % | 98,2 % | 13,8 % | 17,7 % |
| Même codification qu'en août | 89,7 % | 92,9 % | 81,6 % | 96,9 % | 68,1 % | 0 % | 100 % | 0 % | 0 % |

  - **Nouveaux retards** : premiers détectés avec des classes équilibrées (CatBoost 13,8 %, soit 110 sur 799 ; régression logistique 12,6 %) ; RandomForest et le MLP n'en trouvent presque pas.
  - **Contrepartie des classes équilibrées** : CatBoost et la régression logistique passent sous la règle naïve en bonnes prédictions (89,6 % et 89,0 % contre 89,7 %), la famille 0 baisse (92,7 % et 93,3 % contre 96,9 %), les sorties du retard retrouvées aussi (68,9 % et 38,3 %) ; ils attribuent beaucoup plus de niveaux 3 qu'il n'y en a (CatBoost 380 pour 258 vrais, dont 120 justes ; régression logistique 810, dont 165 justes).
  - **Le meilleur score optimisé (CatBoost, 87,01 %)** ne dépasse le MLP et RandomForest que de 0,2 à 0,5 point, dans l'ordre de l'écart-type des plis.
- **Passage 9** (`01e_optimisation_tout_regroupe` : variante du passage 8, cible `PAY_1` **et** variables `PAY_2` à `PAY_6` regroupées en -2, -1, 0, 2 et plus) :

| Modèle | Réglage retenu | Validation (moyenne des 4 familles) | Écart avec le passage 8 | Train | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|---|
| Régression logistique | C = 10, classes équilibrées | 86,32 % ± 0,72 | +0,27 | 86,55 % | 0,26 % | 5 s |
| Arbre de décision | gini, profondeur 8, feuilles 2, classes équilibrées | 86,61 % ± 0,58 | +0,73 | 87,71 % | 1,26 % | 6 s |
| RandomForest | 500 arbres, profondeur 25, feuilles 5, `max_features` 0,5, `balanced_subsample` | 86,98 % ± 0,73 | +0,14 | 93,10 % | 6,57 % | 1 337 s |
| MLP | couches (128, 64), alpha 10⁻⁴ | 86,47 % ± 0,89 | -0,04 | 87,20 % | 0,84 % | 57 s |
| CatBoost | profondeur 5, `learning_rate` 0,03, `l2_leaf_reg` 5, `Balanced` | 87,17 % ± 0,66 | +0,16 | 88,46 % | 1,46 % | 1 194 s |

  Prédictions hors pli sur le train :

| Modèle | Bonnes prédictions | -2 | -1 | 0 | 2 et plus | Sorties du retard (366) | Retards maintenus (1 705) | Nouveaux retards (799) | Changements entre sains (998) |
|---|---|---|---|---|---|---|---|---|---|
| Régression logistique | 89,7 % | 94,8 % | 86,2 % | 94,3 % | 70,0 % | 54,9 % | 98,1 % | 10,0 % | 9,4 % |
| Arbre de décision | 89,6 % | 95,2 % | 88,1 % | 93,2 % | 69,9 % | 68,0 % | 97,8 % | 10,3 % | 15,3 % |
| RandomForest | 91,1 % | 95,2 % | 88,9 % | 96,1 % | 67,8 % | 75,1 % | 97,9 % | 3,5 % | 12,4 % |
| MLP | 91,2 % | 95,2 % | 88,0 % | 97,1 % | 65,7 % | 79,5 % | 96,4 % | 0 % | 19,0 % |
| CatBoost | 90,3 % | 95,0 % | 89,6 % | 94,0 % | 70,1 % | 72,1 % | 97,9 % | 10,9 % | 16,3 % |

  - **Score optimisé** : écarts avec le passage 8 de -0,04 à +0,73 point, sous l'écart-type des plis ou à son niveau (0,58 à 0,89) ; aucune alerte de variance.
  - **CatBoost, moins de fausses alertes** : famille 0 à 94,0 % (92,7 % au passage 8), sorties du retard à 72,1 % (68,9 %), surapprentissage à 1,46 % (3,08 %) ; en contrepartie, 10,9 % de nouveaux retards retrouvés (13,8 %).
  - **Régression logistique** : sorties du retard à 54,9 % (38,3 %), bonnes prédictions au niveau de la règle naïve (89,7 %).
  - **Durées** : CatBoost aussi long qu'au passage 8 malgré quatre classes au lieu de dix ; RandomForest quatre fois plus long (cinq tours, 500 arbres).
- **Passage 10** (`01d_optimisation_cible_regroupee` : variante du passage 8, cible `PAY_1` regroupée en -2, -1, 0, 2 et plus, variables `PAY_2` à `PAY_6` détaillées) :

| Modèle | Réglage retenu | Validation (moyenne des 4 familles) | Train | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|
| Régression logistique | C = 1, classes équilibrées | 86,25 % ± 0,68 | 86,50 % | 0,28 % | 4 s |
| Arbre de décision | entropy, profondeur 8, feuilles 10, classes équilibrées | 86,54 % ± 0,73 | 87,28 % | 0,85 % | 9 s |
| RandomForest | 100 arbres, profondeur illimitée, feuilles 5, `max_features` 0,5, `balanced_subsample` | 86,91 % ± 0,68 | 93,29 % | 6,84 % | 338 s |
| MLP | couche (64), alpha 10⁻³ | 86,30 % ± 0,61 | 86,89 % | 0,69 % | 10 s |
| CatBoost | profondeur 5, `learning_rate` 0,03, `l2_leaf_reg` 3, `Balanced` | 87,13 % ± 0,66 | 88,57 % | 1,63 % | 799 s |

  Prédictions hors pli sur le train :

| Modèle | Bonnes prédictions | -2 | -1 | 0 | 2 et plus | Sorties du retard (366) | Retards maintenus (1 705) | Nouveaux retards (799) | Changements entre sains (998) |
|---|---|---|---|---|---|---|---|---|---|
| Régression logistique | 89,7 % | 94,7 % | 86,1 % | 94,3 % | 69,9 % | 54,4 % | 98,1 % | 9,8 % | 9,2 % |
| Arbre de décision | 89,5 % | 95,2 % | 88,0 % | 93,2 % | 69,8 % | 61,7 % | 98,5 % | 8,6 % | 13,9 % |
| RandomForest | 91,0 % | 95,2 % | 88,8 % | 96,0 % | 67,7 % | 73,2 % | 97,8 % | 3,4 % | 13,3 % |
| MLP | 91,1 % | 94,6 % | 87,4 % | 97,1 % | 66,0 % | 76,2 % | 97,0 % | 0 % | 14,9 % |
| CatBoost | 90,2 % | 95,1 % | 89,5 % | 93,9 % | 70,0 % | 69,9 % | 97,8 % | 10,8 % | 16,8 % |

  - **Comparaison des passages 8, 9 et 10 (CatBoost, meilleur modèle des trois)** : score optimisé 87,01 % (cible détaillée), 87,13 % (cible regroupée), 87,17 % (cible et variables regroupées), écarts sous l'écart-type des plis (0,63 à 0,66). Le regroupement de la cible réduit les fausses alertes (famille 0 : 92,7 % → 93,9 %) et le surapprentissage (3,08 % → 1,63 %) ; regrouper aussi les variables n'y ajoute presque rien (famille 0 : 94,0 % ; sorties du retard : 69,9 % → 72,1 %).
- **Pistes notées pour un prochain essai** : apprendre aussi sur les mois d'avril à août empilés (chaque mois prédit à partir des mois précédents ; notebook `01f`, passage 11) ; essai avec la codification 1 comme classe à prédire (la banque pose-t-elle les 1 selon une logique que le modèle peut apprendre ?).
