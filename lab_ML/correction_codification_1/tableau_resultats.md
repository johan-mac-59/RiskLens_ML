# Correction de la codification 1 par machine learning : journal des résultats

> Essai **bonus et indépendant** des autres branches de machine learning du projet : il n'en reprend aucun choix (variables, encodages, transformations, réglages).
>
> **Ce qui a été retenu pour le projet** : la règle de correction de `PAY_1` (passage 28) et les corrections des codifications 1 d'avril à août (passage 19, sans la règle fixe des impayés) sont reprises dans `src/02_02_modele_sorties_retard.ipynb` et dans le niveau 2 de `src/02_01_nettoyage.ipynb` ; l'étude qui les justifie est `src/05_04_EDA_codification1.ipynb`. Dans le projet, la codification corrigée s'appelle `PAY_1` et celle de la banque `PAY_1_original` ; les notebooks de ce dossier l'appellent `PAY_1_corrigee`.
>
> **Notebooks** : `01_ml_septembre` (machine learning de septembre, sur le niveau 0 tel quel), puis ses variantes `01b_ml_septembre_log` (montants et plafond au logarithme), `01c_optimisation` (boucle d'optimisation), `01d_optimisation_cible_regroupee` (cible regroupée), `01e_optimisation_tout_regroupe` (cible et variables regroupées), `01f_optimisation_mois_empiles` (mois d'avril à septembre empilés) et `01g_codification1_classe` (la codification 1 comme classe) ; `10_corrections_manuelles_anticipees` (codifications 1 d'avril à août) ; `11a` à `11f` (anticipation de `PAY_1`, sorties du retard, entrées en retard, effet sur la prédiction du défaut) ; un brouillon (`brouillon_11f_reglages_fixes`). Les passages gardent leur numéro d'origine.

## 1. Cadre

- **Hypothèse testée, une seule** : la codification 1 est un **code d'attente**, posé par la banque à la place d'une vraie codification qu'elle n'a pas encore tranchée. Si un modèle sait dire ce que cache un 1, l'hypothèse tient ; s'il ne sait pas décider, le 1 est autre chose.
- **Données** : niveau 0 du nettoyage (`data/creditcard_pret_ingestion.csv`, 30 000 clients), sans `dpnm` (jamais utilisé), sans `ID` ; aucune colonne ajoutée.
- **Codifications 1 d'avril à août** (34 valeurs, 28 clients) : leurs 28 clients ont tous `PAY_1` = 1, hors du train et du test ; tranchées en correctif, à appliquer après le machine learning s'il est concluant : par la règle de l'encours nul (21 clients : pas de facture d'août, `BILL_AMT2` <= 0, et juillet sain → codification de juillet) et à la main (7 clients). Décisions et raisons : `10_corrections_manuelles_anticipees` (passage 19).
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
- **Pistes notées pour un prochain essai** : apprendre aussi sur les mois d'avril à août empilés (chaque mois prédit à partir des mois précédents ; notebook `01f`, passage 11) ; essai avec la codification 1 comme classe à prédire (la banque pose-t-elle les 1 selon une logique que le modèle peut apprendre ?) ; notebook `01g`) ; **colonnes ajoutées**, à tester une fois l'importance des variables connue : utilisation du plafond (`ratio_BILL_LIMITn`), ratio de paiement (`ratio_PAY_BILLn`), forte hausse de l'utilisation du plafond au mois de la codification (à définir). Chaque colonne ajoutée est à valider et à documenter dans `docs/colonnes_creees.md`.
- **Passage 11** (`01f_optimisation_mois_empiles` : variante du passage 9 ; les modèles apprennent aussi sur les mois d'avril à août, 119 963 exemples pour 24 737 clients, colonnes rangées par ancienneté ; mêmes 5 plis, notés sur septembre ; score en train calculé lui aussi sur septembre ; régression logistique avec choix de pénalité L1 ; profondeur des arbres plafonnée à 30 ; départ de la boucle aux meilleurs réglages du passage 9). Un premier lancement, interrompu, calculait le score en train sur tous les mois appris : écarté, ses chiffres ne sont pas repris.

| Modèle | Réglage retenu | Validation (moyenne des 4 familles) | Écart avec le passage 9 | Train (septembre) | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|---|
| Régression logistique | C = 0,1, classes équilibrées, pénalité L1 (`l1_ratio` = 1) | 85,49 % ± 0,73 | -0,83 | 85,51 % | 0,02 % | 901 s |
| Arbre de décision | entropy, profondeur 8, feuilles 2, classes équilibrées | 86,75 % ± 0,68 | +0,14 | 87,04 % | 0,32 % | 14 s |
| RandomForest | 300 arbres, profondeur 25, feuilles 10, `max_features` 0,5, `balanced_subsample` | 87,13 % ± 0,75 | +0,15 | 89,73 % | 2,90 % | 6 377 s |
| MLP | couches (128, 64), alpha 10⁻⁵ | 86,73 % ± 0,84 | +0,26 | 87,21 % | 0,56 % | 136 s |
| CatBoost | profondeur 7, `learning_rate` 0,02, `l2_leaf_reg` 5, `Balanced` | 87,31 % ± 0,55 | +0,14 | 87,78 % | 0,54 % | 3 880 s |

  Prédictions hors pli sur le septembre du train (mêmes 21 049 clients que le passage 9) :

| Modèle | Bonnes prédictions | -2 | -1 | 0 | 2 et plus | Sorties du retard (366) | Retards maintenus (1 705) | Nouveaux retards (799) | Changements entre sains (998) |
|---|---|---|---|---|---|---|---|---|---|
| Régression logistique | 88,8 % | 93,7 % | 85,6 % | 93,3 % | 69,4 % | 41,3 % | 97,9 % | 8,5 % | 9,2 % |
| Arbre de décision | 89,6 % | 94,9 % | 89,3 % | 93,0 % | 69,9 % | 69,7 % | 97,3 % | 11,5 % | 16,1 % |
| RandomForest | 91,1 % | 95,0 % | 89,6 % | 95,9 % | 68,0 % | 72,7 % | 98,4 % | 3,1 % | 17,4 % |
| MLP | 91,3 % | 95,2 % | 88,4 % | 97,0 % | 66,4 % | 76,5 % | 97,5 % | 0,1 % | 21,3 % |
| CatBoost | 90,4 % | 95,0 % | 90,4 % | 93,8 % | 70,0 % | 74,6 % | 98,2 % | 9,9 % | 18,9 % |

  **Importance par permutation** (baisse du score en points quand la variable est mélangée ; moyenne des cinq modèles) : `codif_m1` (codification du mois précédent) 47,96 ; `solde_m0` (solde de fin de mois) 6,26 ; toutes les autres colonnes moins de 1 point chacune (`solde_m1` 0,88, `codif_m2` 0,66, `paiement_m0` 0,51, `codif_m3` 0,48, `paiement_m1` 0,36, `LIMIT_BAL` 0,31, les autres 0,13 ou moins). Par ancienneté (somme des colonnes du mois, moyenne des modèles) : M 6,77 ; M-1 49,20 ; M-2 0,83 ; M-3 0,56 ; M-4 0,20 ; M-5 0,21 ; plafond 0,31.

  **Régression logistique, coefficients annulés par la pénalité L1** : aucun pour `codif_m1`, les soldes et paiements de M et M-1, ni le plafond ; 50 à 75 % pour `codif_m2` à `codif_m5` ; 50 % pour `solde_m2`, `paiement_m4` et `paiement_m5`.

  - **Score optimisé** : écarts avec le passage 9 de +0,14 à +0,26 point pour les quatre modèles souples, sous l'écart-type des plis (0,55 à 0,84) ; -0,83 pour la régression logistique ; surapprentissage plus faible pour tous (CatBoost 0,54 %, RandomForest 2,90 %).
  - **Clients qui changent** : CatBoost retrouve 74,6 % des sorties du retard (72,1 % au passage 9) et 9,9 % des nouveaux retards (10,9 %) ; le MLP 76,5 % des sorties (79,5 %).
  - **Importance** : la codification du mois précédent et le solde du mois portent presque toute l'information ; les mois M-2 à M-5 et le plafond pèsent moins de 1 point chacun. L'importance par permutation sous-estime les colonnes redondantes (une autre colonne peut porter la même information).
  - **Durées** : RandomForest 1 h 46, CatBoost 1 h 05, régression logistique 15 min (solveur `saga`).
- **Passage 12** (`01g_codification1_classe` : la codification 1 comme cinquième classe ; base du passage 9 ; les 28 clients avec une codification 1 d'avril à août retirés, 29 972 clients dont 3 660 codifiés 1 en septembre ; découpage propre, 80/20 stratifié sur `PAY_1`, train de 23 977 clients ; score optimisé = moyenne des **cinq** familles, non comparable aux passages précédents ; régression logistique avec choix de pénalité L1 ; profondeur des arbres plafonnée à 30) :

| Modèle | Réglage retenu | Validation (moyenne des 5 familles) | Train | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|
| Régression logistique | C = 10, classes équilibrées, pénalité L1 | 75,66 % ± 0,48 | 75,84 % | 0,25 % | 75 s |
| Arbre de décision | gini, profondeur 8, feuilles 10, classes équilibrées | 76,30 % ± 0,71 | 78,14 % | 2,36 % | 7 s |
| RandomForest | 500 arbres, profondeur 10, feuilles 5, `max_features` 0,5, `balanced_subsample` | 77,75 % ± 0,71 | 81,26 % | 4,32 % | 2 270 s |
| MLP | couches (128, 64), alpha 0,1 | 76,89 % ± 0,29 | 77,93 % | 1,33 % | 57 s |
| CatBoost | profondeur 4, `learning_rate` 0,05, `l2_leaf_reg` 3, `Balanced` | 77,71 % ± 0,57 | 80,85 % | 3,88 % | 613 s |

  Prédictions hors pli sur le train :

| Modèle | Bonnes prédictions | -2 | -1 | 0 | **1** | 2 et plus |
|---|---|---|---|---|---|---|
| Régression logistique | 83,0 % | 86,2 % | 81,6 % | 94,5 % | 59,1 % | 56,9 % |
| Arbre de décision | 83,4 % | 78,0 % | 86,2 % | 92,7 % | 72,0 % | 52,7 % |
| RandomForest | 85,3 % | 80,2 % | 87,7 % | 95,5 % | 71,9 % | 53,5 % |
| MLP | 85,5 % | 76,9 % | 86,7 % | 97,2 % | 73,4 % | 50,3 % |
| CatBoost | 84,6 % | 83,2 % | 88,4 % | 93,8 % | 68,2 % | 55,0 % |
| Même codification qu'en août | 78,7 % | 92,9 % | 81,6 % | 96,9 % | 0 % | 67,7 % |

  **La codification 1** (2 928 vrais 1 dans le train) :

| Modèle | Codifiés 1 par le modèle | Dont vrais 1 | Retrouvés | Précision | 1 posés après un retard (1 467) : retrouvés / précision | 1 posés après une codification saine (1 461) : retrouvés / précision | Vrais 1 ratés, prédits 2 et plus / -2 |
|---|---|---|---|---|---|---|---|
| Régression logistique | 2 547 | 1 731 | 59,1 % | 68,0 % | 50,9 % / 57,4 % | 67,4 % / 79,0 % | 58,6 % / 33,5 % |
| Arbre de décision | 3 095 | 2 107 | 72,0 % | 68,1 % | 62,0 % / 60,5 % | 82,0 % / 75,3 % | 65,2 % / 24,8 % |
| RandomForest | 2 925 | 2 104 | 71,9 % | 71,9 % | 61,1 % / 64,9 % | 82,6 % / 78,3 % | 64,7 % / 23,1 % |
| MLP | 3 038 | 2 149 | 73,4 % | 70,7 % | 57,8 % / 63,9 % | 89,0 % / 76,1 % | 71,4 % / 12,3 % |
| CatBoost | 2 740 | 1 997 | 68,2 % | 72,9 % | 60,2 % / 65,2 % | 76,2 % / 80,4 % | 58,8 % / 30,5 % |

  Les vrais 1 ratés ne sont presque jamais prédits 0 (0,3 à 1,4 %) ni souvent -1 (7,7 à 14,9 %). **Clients qui changent** (hors 1) : sorties du retard retrouvées de 23,2 % (régression logistique) à 64,8 % (MLP), retards maintenus de 70,9 % à 79,2 %, nouveaux retards de 0,1 % (MLP) à 14,6 % (arbre de décision).

  **Importance par permutation** (moyenne des cinq modèles) : `PAY_2` 44,07 ; `BILL_AMT1` 12,39 ; `PAY_3` 3,27 ; `PAY_AMT1` 2,17 ; `BILL_AMT2` 1,65 ; `PAY_AMT2` 1,25 ; les autres moins de 1. Par mois : septembre (M) 14,56 ; août (M-1) 46,97 ; juillet (M-2) 4,29 ; juin 1,48 ; mai 1,68 ; avril 1,36 ; plafond 0,39. **Régression logistique, coefficients annulés (L1)** : 5 % pour `PAY_2`, 15 % pour `PAY_3`, 30 % pour `PAY_4` à `PAY_6`, 20 % pour les montants sauf `BILL_AMT1` et `BILL_AMT2` (0 %).

  - **La codification 1 se prédit en partie** : sept sur dix environ retrouvés par RandomForest et le MLP, avec une précision de 71 à 73 % (RandomForest, MLP, CatBoost) ; mieux pour les 1 posés après une codification saine (76 à 89 % retrouvés, précision 75 à 80 %) que pour ceux posés après un retard (51 à 62 %, précision 57 à 65 %).
  - **Les 1 ratés sont pris pour des retards** (59 à 71 %) ou pour des -2 (12 à 34 %).
  - **Contrepartie** : en ajoutant le 1, la famille 2 et plus tombe sous la règle naïve (50,3 à 56,9 % contre 67,7 %), les retards maintenus aussi (70,9 à 79,2 % contre 100 %), et la famille -2 baisse (76,9 à 86,2 % contre 92,9 %).
  - **Importance** : comme au passage 11, août et septembre portent presque toute l'information ; juillet pèse un peu plus (4,29 contre 0,83).
## 4. Point d'étape (nuit du 9 au 10/10/2026)

**Où on en est**
- Base retenue : `01e` (cible et codifications regroupées en -2, -1, 0, 2 et plus ; montants et plafond au logarithme signé). Meilleur modèle au score optimisé : CatBoost, à égalité avec RandomForest (passages 9 et 11).
- `01f` (mois empilés) : écarts de +0,14 à +0,26 point pour les modèles souples, sous l'écart-type des plis ; moins de surapprentissage ; trois fois plus long.
- `01g` (le 1 comme classe) : la codification 1 se prédit en partie (sept sur dix environ, précision de 71 à 73 % pour RandomForest, le MLP et CatBoost), mieux après une codification saine qu'après un retard.
- Importance (passages 11 et 12) : la codification d'août et le solde de septembre portent presque toute l'information ; juin, mai, avril et le plafond, moins de 1 point chacun.
- Le test n'a été lu dans aucun notebook.

**Suite donnée** : la base retenue pour corriger les `PAY_1` = 1 n'est ni `01e` ni `01f`, mais une règle en deux temps (passage 23) : sain en août → codification d'août ; en retard en août → un modèle des sorties du retard. Règle finale : passage 28.

**Pistes notées** : colonnes ajoutées (utilisation du plafond, ratio de paiement, forte hausse de l'utilisation), à valider et à documenter avant tout essai.

## 5. Constats complémentaires (10/10/2026, analyses descriptives en lecture seule)

*Calculs faits hors notebook, sur le niveau 0, sans les clients du test du ML de septembre (sauf mention). Faits et chiffres seulement ; conclusions à écrire par l'utilisateur.*

**Retards d'août codifiés 1 en septembre** : 46,8 % de tous les retards d'août ; 36,6 % des retards de 3 et plus.

**Défaut (`dpnm`) des clients sains en août et sans solde de septembre** (2 402 clients ; ensemble des clients retenus : 22,6 %) : 25,0 % ; codifiés 1 en septembre, 27,1 % (1 688) ; codifiés -2, 19,9 % (709). Inactifs depuis avril (aucune facture ni paiement) : 36,6 % (858 ; 38,3 % si 1, 32,8 % si -2). Avec une trace d'activité : 18,5 % (1 544 ; 21,1 % si 1, 12,0 % si -2). Sur tout le niveau 0 : `PAY_1` = -2, 13,2 % de défaut (2 759) ; sans solde de septembre, 20,3 % ; comptes sans facture ni paiement sur 6 mois, 36,2 % (941, dont 590 codifiés 1 et 351 codifiés -2).

- **Passage 19** (`10_corrections_manuelles_anticipees` : corrections des 34 codifications 1 d'avril à août) :
  - règles, dans l'ordre : (0) règle de l'utilisateur, `PAY_n` = 1 et solde du mois suivant nul ou créditeur (`BILL_AMT(n-1)` <= 0) → codification saine antérieure ; (1) encours nul, `PAY_n` = 1 sans facture du mois (`BILL_AMTn` <= 0) et mois précédent sain → codification du mois précédent ; (2) règle fixe des impayés (une facture du mois d'au moins 100 NT$ sans aucun paiement le mois suivant vaut un retard ; abandonnée depuis) ; (3) décisions à la main.
  - **Décisions de l'utilisateur** : 6783 → 0 (juin, juillet, août) ; 11498 → 2 (juin, juillet, août) ; 892 → 0 (juillet, août) ; 1967 → 0 (juillet, août) ; 5645 → 0 (août) ; 19195 → 2 (août) ; 25176 → 2 (août).
  - **Repris dans le projet** : règles (0) et (1) et décisions à la main, sans la règle fixe des impayés : `src/02_02_modele_sorties_retard.ipynb` (section 2) et niveau 2 de `src/02_01_nettoyage.ipynb` ; raisons des décisions dans `src/05_04_EDA_codification1.ipynb` (section 3).

- **Passage 20** (`11a_anticipation_pay1` : variante du passage 11, mois empilés ; codifications d'avril à août corrigées par le `10` (règles, règle fixe des impayés comprise, et décisions) avant tout apprentissage : 21 par l'encours nul, 13 par les décisions, 2 008 par la règle fixe, soit avril 558, mai 897, juin 520, juillet 23, août 44 ; `PAY_1` non corrigé ; 119 997 exemples pour 24 737 clients ; mêmes 5 plis, notés sur septembre ; départ de la boucle aux meilleurs réglages du passage 11 ; modèles enregistrés dans `modeles/11a/`) :

| Modèle | Réglage retenu | Validation (moyenne des 4 familles) | Écart avec le passage 11 | Train (septembre) | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|---|
| Régression logistique | C = 0,1, classes équilibrées, pénalité L1 (`l1_ratio` = 1) | 85,24 % ± 0,71 | -0,25 | 85,28 % | 0,04 % | 42 s |
| Arbre de décision | gini, profondeur 8, feuilles 20, classes équilibrées | 86,64 % ± 0,47 | -0,11 | 86,87 % | 0,27 % | 54 s |
| RandomForest | 300 arbres, profondeur 25, feuilles 20, `max_features` 0,5, `balanced_subsample` | 87,01 % ± 0,74 | -0,12 | 88,16 % | 1,30 % | 4 349 s |
| MLP | couches (128, 64), alpha 10⁻⁶ | 86,53 % ± 0,61 | -0,20 | 87,10 % | 0,66 % | 85 s |
| CatBoost | profondeur 8, `learning_rate` 0,03, `l2_leaf_reg` 10, `Balanced` | 87,18 % ± 0,59 | -0,13 | 88,03 % | 0,96 % | 6 161 s |

  Prédictions hors pli sur le septembre du train (mêmes 21 049 clients ; les effectifs des changements bougent un peu, car la codification d'août est corrigée pour certains clients) :

| Modèle | Bonnes prédictions | -2 | -1 | 0 | 2 et plus | Sorties du retard (380) | Retards maintenus (1 706) | Nouveaux retards (798) | Changements entre sains (998) |
|---|---|---|---|---|---|---|---|---|---|
| Régression logistique | 89,0 % | 93,2 % | 86,2 % | 93,8 % | 67,8 % | 52,6 % | 97,0 % | 5,3 % | 8,2 % |
| Arbre de décision | 89,4 % | 94,5 % | 89,5 % | 92,5 % | 70,0 % | 64,7 % | 98,2 % | 9,8 % | 19,4 % |
| RandomForest | 91,0 % | 94,6 % | 89,7 % | 95,6 % | 68,1 % | 69,2 % | 98,4 % | 3,5 % | 16,6 % |
| MLP | 91,2 % | 94,7 % | 88,0 % | 97,1 % | 66,3 % | 75,0 % | 97,2 % | 0,1 % | 21,0 % |
| CatBoost | 90,7 % | 94,6 % | 90,3 % | 94,7 % | 69,0 % | 73,7 % | 98,1 % | 7,0 % | 19,1 % |
| Règle « même codification qu'en août » | 89,7 % | 92,5 % | 81,5 % | 96,8 % | 68,1 % | 0,0 % | 100,0 % | 0,0 % | 0,0 % |

  **Régression logistique, coefficients annulés par la pénalité L1** : aucun pour `codif_m1`, les soldes et paiements de M à M-3, ni le plafond ; 50 à 60 % pour `codif_m2` à `codif_m5` ; 50 % pour `solde_m4` et `paiement_m4`, 75 % pour `paiement_m5`.

  - **Score optimisé** : écarts avec le passage 11 de -0,11 à -0,25 point pour les cinq modèles, tous sous l'écart-type des plis (0,47 à 0,74) : dans le bruit. Surapprentissage plus faible pour le RandomForest (1,30 % contre 2,90 %).
  - **Clients qui changent** : la régression logistique retrouve plus de sorties du retard (52,6 % contre 41,3 %) ; CatBoost 73,7 % (74,6 %), MLP 75,0 % (76,5 %), RandomForest 69,2 % (72,7 %), arbre 64,7 % (69,7 %). Nouveaux retards : 0,1 à 9,8 % (0,1 à 11,5 % au passage 11).
  - **Importance par permutation** (baisse du score en points, moyenne des cinq modèles) : `codif_m1` 47,22 (47,96 au passage 11) ; `solde_m0` 6,38 (6,26) ; toutes les autres colonnes moins de 1 point (`solde_m1` 0,95, `codif_m2` 0,54, `codif_m3` 0,43, `paiement_m1` 0,43, `paiement_m0` 0,41, `solde_m2` 0,24, `LIMIT_BAL` 0,20, les autres 0,12 ou moins). Par ancienneté : M 6,79 ; M-1 48,60 ; M-2 0,85 ; M-3 0,52 ; M-4 0,12 ; M-5 0,17 ; plafond 0,20. Les mois corrigés surtout par la règle fixe des impayés (avril à juin, soit M-3 à M-5 pour septembre) pèsent toujours moins de 1 point.
  - **Durées** : CatBoost 1 h 43, RandomForest 1 h 12, régression logistique 42 s.

- **Passage 22** (`11b_anticipation_pay1_binaire` : variante du passage 9, septembre seul, sans empilement ni correctifs ; cible `PAY_1` binaire, sain (-2, -1, 0) ou en retard (2 et plus) : 18 545 sains et 2 504 retards dans le train ; score optimisé = moyenne des taux de bonne classe des deux classes, **non comparable** aux passages à quatre familles ; départ de la boucle aux meilleurs réglages du passage 9 ; modèles enregistrés dans `modeles/11b/` ; durée totale 34 min) :

| Modèle | Réglage retenu | Validation (moyenne des 2 classes) | Train | Surapprentissage (relatif) | Durée |
|---|---|---|---|---|---|
| Régression logistique | C = 1, classes équilibrées, `l1_ratio` 0,5 | 83,94 % ± 1,07 | 84,07 % | 0,15 % | 31 s |
| Arbre de décision | entropy, profondeur 4, feuilles 2, classes équilibrées | 84,22 % ± 0,89 | 84,37 % | 0,17 % | 9 s |
| RandomForest | 500 arbres, profondeur 20, feuilles 50, `max_features` sqrt, `balanced_subsample` | 84,21 % ± 0,85 | 85,42 % | 1,41 % | 1 569 s |
| MLP | couches (256, 128), alpha 10⁻³ | 82,86 % ± 0,77 | 83,27 % | 0,49 % | 18 s |
| CatBoost | profondeur 4, `learning_rate` 0,03, `l2_leaf_reg` 10, `Balanced` | 84,45 % ± 0,95 | 86,19 % | 2,01 % | 317 s |
| Règle « même codification qu'en août » (même mesure) | — | 83,05 % | — | — | — |

  Prédictions hors pli sur le train (mêmes 21 049 clients que le passage 9), avec le passage 9 entre parenthèses :

| Modèle | Bonnes prédictions | Sains | 2 et plus | Sorties du retard (366) | Retards maintenus (1 705) | Nouveaux retards (799) |
|---|---|---|---|---|---|---|
| Régression logistique | 91,6 % | 94,0 % | 73,8 % (70,0) | 1,4 % (54,9) | 100,0 % (98,1) | 18,0 % (10,0) |
| Arbre de décision | 93,5 % | 96,4 % | 72,0 % (69,9) | 37,4 % (68,0) | 99,6 % (97,8) | 13,1 % (10,3) |
| RandomForest | 93,3 % | 96,1 % | 72,3 % (67,8) | 14,2 % (75,1) | 99,8 % (97,9) | 13,5 % (3,5) |
| MLP | 95,6 % | 99,5 % | 66,2 % (65,7) | 78,1 % (79,5) | 97,0 % (96,4) | 0,5 % (0) |
| CatBoost | 92,8 % | 95,5 % | 73,4 % (70,1) | 30,6 % (72,1) | 99,6 % (97,9) | 17,5 % (10,9) |
| Règle « même codification qu'en août » | 94,5 % | 98,0 % | 68,1 % | 0 % | 100 % | 0 % |

  **Importance par permutation** (baisse du score en points, moyenne des cinq modèles) : `PAY_2` 30,78 ; `PAY_3` 1,00 ; `PAY_5` 0,67 ; `LIMIT_BAL` 0,64 ; `PAY_AMT2` 0,50 ; `BILL_AMT2` 0,45 ; toutes les autres 0,29 ou moins, dont `BILL_AMT1` (solde de septembre) 0,24. Par mois : septembre 0,32 ; août 31,73 ; juillet 1,39 ; juin 0,54 ; mai 0,81 ; avril 0,46 ; plafond 0,64.

  - **Score optimisé** : les modèles dépassent la règle naïve de 1,4 point au plus (CatBoost 84,45 % contre 83,05 %), à peine plus que l'écart-type des plis (0,77 à 1,07).
  - **Changement d'équilibre, pas gain de qualité** : avec deux classes, le retard pèse la moitié du score (un quart avec quatre familles). Les modèles gardent donc presque tous les clients en retard en août dans le retard : retards maintenus 99,6 à 100 %, nouveaux retards mieux retrouvés (CatBoost 17,5 % contre 10,9 %), mais les sorties du retard s'effondrent (CatBoost 30,6 % contre 72,1 % ; régression logistique 1,4 % contre 54,9 %). Le MLP fait l'inverse (78,1 % des sorties, 0,5 % des nouveaux retards).
  - **Importance** : le solde de septembre (`BILL_AMT1`) ne pèse plus que 0,24 point, contre environ 6 au passage 11 ; il servait surtout à séparer -2, -1 et 0 (solde nul ou non), distinction que la cible binaire ne demande plus.

- **Passage 23** (`11c_sorties_du_retard` : règle de l'utilisateur pour estimer les `PAY_1` = 1, sain en août → reste sain, en retard en août → un modèle décide sortie ou retard maintenu ; exemples = clients en retard le mois précédent, mois cibles septembre (2 071, dont 366 sorties), août (3 597) et juillet (2 985), 8 653 exemples dont 2 185 sorties ; empilement limité à juillet par la pratique stable de la banque ; colonnes relatives du `11a`, sans correctifs ; plis par client, notés sur septembre ; critère : précision moyenne sur les sorties ; MLP moyenné sur 5 graines (retenu) face à CatBoost (challenger) ; seuil fixé à l'avance par l'utilisateur, **précision marginale de 80 %** sur les 50 derniers annoncés, calculé dans des plis internes) :

| Modèle | Réglage retenu | Précision moyenne sur les sorties | ROC AUC | Surapprentissage (relatif) | Sorties retrouvées (80 %) | Précision des sorties annoncées (80 %) | Précision marginale en validation (50 clients) |
|---|---|---|---|---|---|---|---|
| MLP | couches (256, 128, 64), alpha 10⁻⁴ | 88,1 % ± 1,3 | 0,957 | 4,70 % | 73,8 % ± 4,1 | 90,5 % ± 2,9 | 82 % |
| CatBoost | profondeur 5, `learning_rate` 0,02, `l2_leaf_reg` 1, `Balanced` | 88,8 % ± 1,4 | 0,960 | 6,71 % | 77,6 % ± 6,5 | 90,0 % ± 3,8 | 78 % |

  - **Duel, pli par pli** : sorties retrouvées -3,8 ± 5,3 points pour le MLP (dans le bruit) ; précision des sorties annoncées +0,5 ± 3,2 (dans le bruit) ; précision moyenne -0,6 ± 0,4 (CatBoost devant, 4 plis sur 5).
  - **Accord** (septembre du train) : 289 sorties annoncées par les deux, dont 91,3 % de vraies ; 28 par CatBoost seul (71,4 % de vraies) ; 10 par le MLP seul (60,0 %) ; parmi les 1 744 non annoncés, 76 vraies sorties (4,4 %).
  - **Niveaux pour information** : à 70 %, 76,0 % (MLP) et 80,9 % (CatBoost) des sorties retrouvées ; à 90 %, 28,4 % ± 16,5 (MLP, seuil instable) et 55,5 % (CatBoost).
  - **Face au `11b`** (MLP, toutes les codifications, environ 78 % des sorties retrouvées pour une précision estimée d'environ 85 %) : le modèle spécialisé annonce des sorties plus fiables (90 %) pour une part retrouvée un peu plus basse, fixée par la règle à la marge.
  - **Importance** (baisse de la précision moyenne, points) : le solde et le paiement du mois et du mois précédent portent le modèle (MLP : `solde_m0` 7,87, `solde_m1` 6,99, `paiement_m0` 3,45 ; CatBoost : `solde_m1` 10,10, `paiement_m0` 6,16) ; les codifications anciennes 0,4 à 1,9.
  - **Application aux 1 824 `PAY_1` = 1 en retard en août** : 140 annoncés sortis par le MLP (7,7 %), 184 par CatBoost (10,1 %), 132 par les deux ; contre 14,5 et 15,5 % sur le septembre du train. Probabilité de sortie médiane plus haute chez les 1 (MLP 0,032 contre 0,020 ; CatBoost 0,114 contre 0,058) : moins de sorties nettes, plus de cas intermédiaires. Modèles et seuils dans `modeles/11c/`.

- **Passage 24** (`11d_entrees_en_retard` : clients du train sains en août, 18 978 dont 799 entrées en retard en septembre (4,2 %) ; entrées selon la codification d'août : -2, 0 sur 2 051 ; -1, 95 sur 4 329 ; 0, 704 sur 12 598 ; septembre seul, historique complet, variables du `11b`, sans correctifs ; trois spécialistes, MLP moyenné sur 5 graines, CatBoost, RandomForest ; critère : précision moyenne sur les entrées ; seuil fixé à l'avance par l'utilisateur, **précision marginale de 50 %** sur les 50 derniers annoncés ; vote à 2 voix sur 3) :

| Modèle | Réglage retenu | Précision moyenne sur les entrées (validation) | Train | Surapprentissage (relatif) | ROC AUC | Entrées annoncées à 50 % |
|---|---|---|---|---|---|---|
| MLP | couches (256, 128, 64), alpha 10⁻³ | 12,66 % ± 1,15 | 12,42 % | -1,92 % | 0,724 | 0 |
| CatBoost | profondeur 3, `learning_rate` 0,02, `l2_leaf_reg` 15, `Balanced` | 13,72 % ± 0,71 | 21,64 % | 36,60 % (aucun réglage admis) | 0,771 | 0 |
| RandomForest | 300 arbres, profondeur 15, feuilles 50, `max_features` sqrt | 14,00 % ± 1,53 | 25,63 % | 45,37 % (aucun réglage admis) | 0,769 | 0 |

  - **Aucune entrée en retard annoncée**, par aucun modèle : dans tous les plis internes, même les 50 clients les plus probables comptaient moins d'une entrée en retard sur deux (seuil infini). Appliqués aux 1 836 `PAY_1` = 1 sains en août : 0 annoncé.
  - **Capacité de tri** : précision moyenne de 12,7 à 14,0 %, environ trois fois le hasard (4,2 %), ROC AUC 0,72 à 0,77 ; le tri existe, mais aucun groupe de clients n'atteint une entrée sur deux.
  - **Surapprentissage de CatBoost et du RandomForest** : la boucle s'arrête au premier tour quand aucun réglage n'est admis, sans pousser vers des réglages plus simples (profondeur 2, feuilles au-delà de 50 non essayées) ; l'écart relatif est aussi gonflé par des scores bas (8 à 12 points d'écart absolu).
  - **Importance** : `PAY_3` (codification de juillet) 2,65 en moyenne, puis le plafond 1,75 ; par mois, juillet pèse le plus (3,08) ; un retard passé reste le principal signal.
  - Probabilité médiane plus basse chez les 1 que dans le train (MLP 0,002 contre 0,036) : les 1 sains en août sont à -2 ou -1 en août (1 833 sur 1 836), d'où l'on entre très rarement en retard.

- **Passage 25** (`11e_pay1_corrigee_defaut` : prédiction du défaut aux préréglages d'`essai_jeu_de_base`, 30 000 clients, test du ML inclus, mêmes 5 plis ; codifications 1 d'avril à août corrigées par le `10` sans la règle des retards (34 codifications, 28 clients) ; **`PAY_1_corrigee` ajoutée à côté de `PAY_1`**, encodée comme les autres `PAY_n` (nombre mis à l'échelle) ; plafond au logarithme ; variantes « Complet + PAY_1 corrigée » (24) et « PAY_n seuls + PAY_1 corrigée » (7) ; comparaison pli par pli avec `jeu_de_base.csv`) :
  - **`PAY_1_corrigee`** : 132 sorties estimées -1, 1 695 retards maintenus à 2 (dont 60 annoncés sortis par un seul modèle), 1 861 sains en août à leur codification d'août (-2 : 1 233 ; -1 : 621 ; 0 : 7).
  - **Ce que regardent les modèles** (perte de précision moyenne, colonne mélangée seule, variante complète) : régression logistique `PAY_1_corrigee` 0,064 contre `PAY_1` 0,034 ; RandomForest 0,049 contre 0,058 ; CatBoost 0,028 contre 0,073 ; MLP 0,017 contre 0,146. Part de la famille `PAY_1_corrigee` dans la perte totale : 22,0 % (régression logistique), 17,2 % (RandomForest), 8,9 % (CatBoost), 5,4 % (MLP).
  - **Précision face à `essai_jeu_de_base`** : meilleur contre meilleur (CatBoost) dans le bruit, précision moyenne 55,6 % des deux côtés, précision aux rappels de 50 à 70 % de -0,29 à +0,03 point, +0,36 au rappel de 80 % (gain réel, 4 plis sur 5). **Régression logistique : gain réel** sur 5 plis sur 5 (précision moyenne +0,46, précision au rappel de 50 % +1,20, rappel à la règle marginale +8,79 points pour -1,82 de précision). MLP dans le bruit partout ; RandomForest mitigé (précision moyenne +0,37, précision aux rappels de 60 à 80 % de -0,27 à -0,58).
  - **Lecture** : la régression logistique, qui lit `PAY_1` comme une échelle, préfère la version corrigée (un 1 placé entre 0 et 2 ne correspond pas à son sens d'attente) ; les modèles non linéaires (CatBoost, MLP) tirent déjà du 1 d'origine ce qu'il dit, et gardent `PAY_1` en premier. Le meilleur modèle ne gagne rien. Le plafond au logarithme est une autre différence avec `essai_jeu_de_base` ; il pèse 0,2 à 1,4 point de perte, peu susceptible d'expliquer l'écart de la régression logistique.

- **Passage 26** (`11f_pay1_origine_ou_corrigee` : prédiction du défaut, 30 000 clients, test du ML inclus, mêmes 5 plis ; deux versions de 23 variables, **`PAY_1` d'origine** ou **`PAY_1_corrigee` à sa place** ; codifications 1 d'avril à août corrigées par le `10` dans les deux ; **toutes les codifications en catégories** ; paiements et plafond au logarithme, factures au logarithme signé, données démographiques incluses ; boucle d'`essai_jeu_de_base` lancée séparément pour chaque version, grilles de départ élargies ; règle marginale 1 pour 1) :

| Modèle | Précision moyenne, `PAY_1` d'origine | Précision moyenne, `PAY_1_corrigee` | Écart (points) | Précision aux rappels de 50 / 60 / 70 / 80 % (écart, points) |
|---|---|---|---|---|
| Régression logistique (C = 1 dans les deux) | 54,6 % | 52,4 % | -2,24 ± 0,28 (0 pli sur 5) | -0,15 / -0,51 / -0,51 / -0,30 |
| MLP | 55,2 % | 53,5 % | -1,65 ± 0,64 (0 sur 5) | -1,00 / -0,10 / -0,18 / +0,59 |
| RandomForest | 54,8 % | 52,9 % | -1,94 ± 0,35 (0 sur 5) | +0,00 / -0,45 / +0,28 / +0,21 |
| CatBoost (meilleur des deux côtés) | 55,3 % | 53,9 % | -1,36 ± 0,53 (0 sur 5) | -0,83 / -0,22 / -0,56 / +0,06 |

  - **Remplacer `PAY_1` par `PAY_1_corrigee` fait perdre** de la précision moyenne à tous les modèles, sur tous les plis (-1,4 à -2,2 points) ; ROC AUC -0,000 à -0,005. La perte se concentre en tête de liste (précision moyenne) ; aux rappels de 60 à 80 %, les écarts restent sous 0,6 point.
  - **Lecture** : encodé en catégorie, le 1 d'origine forme un groupe à part, que les modèles exploitent ; la correction le fond dans -2, -1 ou 2 et efface cette information. Le 1 porte donc, pour le défaut, une information propre que la correction ne restitue pas.
  - **Importance** (colonne mélangée seule) : la codification de septembre porte l'essentiel dans les deux versions (`PAY_1` 0,128 à 0,189 ; `PAY_1_corrigee` 0,125 à 0,216) ; les autres colonnes 0,016 ou moins.
  - **Face à `essai_jeu_de_base`** (version `PAY_1` d'origine contre variante complète, probabilités hors pli enregistrées, mêmes clients et mêmes plis ; différences : codifications en catégories, plafond au logarithme, grilles élargies, 34 codifications 1 d'avril à août corrigées) : régression logistique, gain réel sur 5 plis sur 5 (précision moyenne +4,68 ± 0,86 points ; précision aux rappels de 50 à 80 % de +2,60 à +4,35) ; MLP, précision moyenne +1,15 ± 0,74 (4 plis sur 5), précision à rappel égal dans le bruit (+0,06 à +0,52) ; RandomForest dans le bruit (-0,43 à +0,21) ; CatBoost dans le bruit (précision moyenne -0,33 ± 0,33), sauf +0,42 ± 0,38 au rappel de 80 % (5 plis sur 5). Le gain de la régression logistique tient à l'encodage en catégories : en nombres, elle ne peut pas lire des codifications dont le risque ne suit pas l'ordre (-2, -1, 0, 1) ; les modèles à base d'arbres trouvent déjà ces groupes seuls.

- **Passage 28** (`11c_sorties_du_retard`, section 9 ajoutée : précision marginale de 50 % pour chaque modèle, décision de l'utilisateur ; quatre candidats arbitres d'autres familles réglés par la boucle ; septembre du train, 2 071 clients en retard en août, dont 366 sorties) :
  - **Candidats** (précision moyenne sur les sorties, validation) : SVM 88,00 % ± 2,04 (C = 1, `gamma` 0,03, classes équilibrées ; retenu comme arbitre), KNN 82,70 % (30 voisins), régression logistique 80,46 % (C = 0,1, L1), bayésien naïf 68,31 % ; pour comparaison, MLP 88,1 %, CatBoost 88,8 %.
  - **Règles à 50 %** : MLP seul 367 sorties annoncées, précision 82,0 %, 82,2 % des sorties retrouvées ; CatBoost seul 369, 82,7 %, 83,3 % ; SVM seul 376, 81,1 %, 83,3 % ; **deux sur deux** (MLP et CatBoost) 343, 86,3 %, 80,9 % ; **deux sur trois** 368, 82,6 %, 83,1 % ; rappel, deux sur deux à 80 % : 289, 91,3 %, 72,1 %.
  - **Sorties estimées chez les 1 824 `PAY_1` = 1 en retard en août** : deux sur deux à 80 %, 132 (7,2 %) ; deux sur deux à 50 %, 185 (10,1 %) ; deux sur trois à 50 %, 220 (12,1 %) ; CatBoost seul, 258 (14,1 %).
  - **Recoupement** (septembre du train) : 337 clients annoncés par les trois modèles (87,2 % de vraies sorties) ; les autres combinaisons sont petites et peu précises (MLP + SVM 17 clients, 23,5 % ; CatBoost + SVM 8, 50,0 % ; MLP + CatBoost 6, 33,3 % ; un seul modèle 7 à 18 clients, 14 à 28 %). Les trois modèles annoncent presque les mêmes clients ; les cas de désaccord sont en majorité de faux positifs. Chez les 1 : 185 annoncés par les trois, 31 par CatBoost et SVM, 42 par CatBoost seul.
  - Six modèles enregistrés dans `modeles/11c/` avec leur seuil à 50 % (`11c_synthese_50.json`).
  - **Trois sur trois à 50 %** (MLP, CatBoost et SVM d'accord) : 337 sorties annoncées, 294 vraies (87,2 %), 80,3 % des sorties retrouvées ; 185 sorties estimées chez les 1 824 `PAY_1` = 1 en retard en août (10,1 %), contre 132 avec la règle à 80 % (+53 clients, +40 %).
  - **Décision de l'utilisateur : règle « trois sur trois »**, précision marginale de 50 % pour chaque modèle (MLP, CatBoost, SVM). Reportée dans `src/02_02_modele_sorties_retard.ipynb` (SVM ajouté, seuils à 50 %, trois voix nécessaires, vérification sur le test et réapprentissage sur train + test à relancer), dans la fonction du niveau 2 de `src/02_01_nettoyage.ipynb` et dans `docs/colonnes_creees.md`.

- **Décision de l'utilisateur (10/10/2026) : la correction des `PAY_1` est conservée**, et la codification de la banque est gardée à côté. Dans le projet (`src/02_01_nettoyage.ipynb`, niveau 2) : `PAY_1` = codification corrigée, `PAY_1_original` = codification de la banque ; la correction se fait avant le repérage de la population en incident ; les modèles sont réappris et enregistrés par `src/02_02_modele_sorties_retard.ipynb` (`src/modeles_pay1/`) ; définitions dans `docs/colonnes_creees.md` (section 0). Repères pour le machine learning : sur les 30 000 clients, remplacer `PAY_1` par la version corrigée fait perdre (passage 26) ; les mettre côte à côte ne coûte rien (passage 25). Ces deux passages ont été faits avec l'ancienne règle de sortie (MLP et CatBoost d'accord, 80 %) : à refaire avec la règle finale.

- **Pistes notées (10/10/2026)** : scénario suivant possible, prédire le **passage** plutôt que la codification : reste en retard, revient sain, reste sain, part en retard (proche de « va-t-il faire défaut », mais plus nuancé : un payeur partiel ne sort pas forcément du retard, et inversement) ; l'estimation serait ensuite retranscrite en codification. Une colonne `PAY_1_estime` (codification estimée pour les 1, `PAY_1` pour les autres) et sa confiance, ajoutées **à côté** de `PAY_1`, diraient au modèle de défaut si la correction apporte une information.
