# 📐 Journal des scénarios du machine learning

> Ce journal suit le machine learning actuel, redémarré après la définition de la population contentieuse. La première itération, entraînée sur le dataset **avec** la population contentieuse, est archivée dans [`1ere_iteration/`](1ere_iteration/) avec son propre journal ([`1ere_iteration/tableau_ML.md`](1ere_iteration/tableau_ML.md)) ; elle reste la référence de performance à battre.

## 1. Données et méthode

⚠️ **Après un clone du dépôt** : les fichiers produits par les lancements (train et test, probabilités hors pli, fichier de résultats, modèles) ne sont pas dans le dépôt. Les sorties des notebooks se lisent telles quelles, mais pour relancer ou comparer un scénario, il faut d'abord exécuter `creation_datasets_ML`, puis les scénarios précédents dans l'ordre : voir la section 0 de la méthodologie.

La méthode commune à tous les scénarios (données, étalon, validation, boucle d'optimisation, raisons d'arrêt, alertes, fichiers enregistrés, évaluation finale) est décrite dans [`methodologie_ML.md`](methodologie_ML.md). En bref :

* **Données** : périmètre S12 sans les clients au contentieux à M, découpage 80/20 propre au ML ([`creation_datasets_ML.ipynb`](creation_datasets_ML.ipynb)) ; le test n'est lu qu'une seule fois, à la toute fin du machine learning, une fois tous les scénarios faits et le modèle final figé (jamais dans un notebook de scénario).
* **Étalon** : la **précision des défauts prédits, au taux de rappel minimal** (objectif : détecter 60 % des défauts hors contentieux ; bilan de l'évaluation finale : objectif trop ambitieux en précision, environ un client signalé sur quatre réellement en défaut, d'où une présentation finale par niveaux de risque), en validation croisée à 5 plis sur le train, avec son écart-type ; un gain plus petit que l'écart-type n'est pas retenu. Elle se compare au taux de défaut du train (environ 16 %), précision d'un tri au hasard.
* **Hyperparamètres** : boucle automatique de GridSearch, sous contrainte de surapprentissage, jusqu'à stabilisation du modèle.
* **Un notebook par scénario** : `ml_0`, `ml_1`… Chaque scénario part du précédent retenu et ajoute un petit groupe de colonnes.

## 2. Scénarios

| Scénario | Ce qui change | Variables | Étalon | Meilleur modèle | Scores (val) | Défauts détectés / précision (val) | Décision |
|---|---|---|---|---|---|---|---|
| [`ml_0_etalon`](ml_0_etalon.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles ; ajustement à la main (04/10/2026) | 23 | Moyenne du F2 au seuil de 0,5 et du ROC AUC (méthode v0) | CatBoost (⚠️ surapprentissage 0,068), à égalité avec RandomForest (0,5949 ± 0,0136, ✅ 0,037) | 0,5981 ± 0,0130 | CatBoost : 1 822 sur 3 084 (59,1 %) / 27,9 % ; RandomForest : 1 850 (60,0 %) / 26,9 % | Point de départ ; les meilleurs modèles trouvent déjà environ 60 % des défauts |
| [`ml_0`](ml_0.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles | 23 | Classement : score décisionnel F2 ; réglage : précision des défauts prédits (taux de rappel minimal 60%, méthode v9) | CatBoost (écart relatif train - val 6,8 %), à égalité avec SVM, MLPClassifier, KNN, LogisticRegression | score décisionnel F2 0,446 ± 0,006 ; précision 22,0 % ± 0,7 pts ; ROC AUC 0,684 | 1 489 sur 2 481 (60,0 %) / 21,9 %, 37,8 % des clients signalés | **Retenu, socle** (v9) : cinq modèles à égalité, RandomForest juste en dessous ; précision d'environ 22 % à 60 % de rappel, pour 13,8 % au hasard |
| [`ml_1`](ml_1.ipynb) | ajout de PAY_1_original (codification de septembre posée par la banque, avec ses codifications 1) ; 6 modèles | 24 | Classement : score décisionnel F2 ; réglage : précision des défauts prédits (taux de rappel minimal 60%, méthode v9) | CatBoost (écart relatif train - val 6,7 %), à égalité avec SVM | score décisionnel F2 0,447 ± 0,005 ; précision 22,1 % ± 0,6 pts ; ROC AUC 0,684 | 1 489 sur 2 481 (60,0 %) / 22,0 %, 37,8 % des clients signalés | **Écarté, à reprendre en phase finale** : dans le bruit pour les six modèles face à `ml_0` (meilleur contre meilleur, CatBoost 0,446 → 0,447, 4 plis sur 5) ; population faible (`PAY_1_original` ne diffère de `PAY_1` que pour 1,6 % des clients du train, sous le seuil de 2 %) ; la référence reste `ml_0` |
| [`ml_2`](ml_2.ipynb) | Scénario complet : toutes les colonnes validées pour le ML (historique des retards : famille incident et famille retard isolé) ; 6 modèles | 53 | Classement : score décisionnel F2 ; réglage : précision des défauts prédits (taux de rappel minimal 60%, méthode v9) | CatBoost (écart relatif train - val 5,6 %), à égalité avec LogisticRegression, SVM, MLPClassifier, KNN, RandomForest | score décisionnel F2 0,452 ± 0,009 ; précision 22,7 % ± 1,1 pts ; ROC AUC 0,693 | 1 489 sur 2 481 (60,0 %) / 22,5 %, 36,9 % des clients signalés | **Retenu, nouvelle référence et point de départ de l'élagage** : gain réel face à `ml_0` en meilleur contre meilleur (CatBoost 0,446 → 0,452, 4 plis sur 5) et pour le SVM (+0,003, 5 plis sur 5) ; gains dans le bruit pour les quatre autres modèles ; les six modèles à égalité ; `CUMUL_INCIDENT` en tête des importances (CatBoost et régression logistique) |
| [`ml_3`](ml_3.ipynb) | ml_2 sans les codifications brutes (PAY_1 à PAY_6, PAY_habituel) : le comportement du client, lu au travers des indicateurs de retard et d'incident ; 6 modèles | 46 | Classement : score décisionnel F2 ; réglage : précision des défauts prédits (taux de rappel minimal 60%, méthode v9) | CatBoost (écart relatif train - val 6,1 %), à égalité avec LogisticRegression, SVM, KNN, MLPClassifier | score décisionnel F2 0,453 ± 0,009 ; précision 22,8 % ± 1,1 pts ; ROC AUC 0,692 | 1 489 sur 2 481 (60,0 %) / 22,3 %, 37,1 % des clients signalés | **Retenu, nouvelle référence (point de départ de l'élagage)** : dans le bruit face à `ml_2` pour les six modèles (meilleur contre meilleur, CatBoost 0,452 → 0,453, 3 plis sur 5) : une fois les retards et les incidents tagués par nos indicateurs, les codifications brutes n'apportent plus rien ; score égal avec 46 variables au lieu de 53 ; `CUMUL_INCIDENT` en tête des importances. Une fois les deux populations à risque écartées par les règles métier, le comportement du client suffit à trier les clients restants par niveau de risque |


## 3. Évaluation finale (une seule fois, sur le test)

**Fait le 07/10/2026** ([`evaluation_finale_test.ipynb`](evaluation_finale_test.ipynb)), test lu une seule fois, protocole commité avant la lecture. Version finale : `ml_14` (21 variables), modèle de décision CatBoost, seuil fixé sur les probabilités hors pli du train au rappel minimal de 60 %.

| Mesure | Validation (train, hors pli) | Test | Intervalle à 95 % (test) |
|---|---|---|---|
| Rappel | 60,0 % | 60,8 % | 57,4 – 64,2 % |
| Précision des défauts prédits | 27,3 % | 28,3 % | 26,1 – 30,4 % |
| Clients signalés | 35,0 % | 34,3 % | 33,0 – 35,7 % |
| Score décisionnel F2 | 0,484 | 0,494 | 0,467 – 0,521 |
| ROC AUC | 0,705 | 0,710 | 0,690 – 0,730 |

Sur le test (4 840 clients, 771 défauts) : 469 défauts détectés, 1 191 fausses alertes, 302 défauts manqués. Autres modèles, pour information (F2 test) : RandomForest 0,493, MLP 0,492, régression logistique 0,487. Au rappel de 44 % (repère de la première itération) : précision de 34,7 % sur le test, contre 38,5 % pour la première itération (indicatif : population et découpage différents).

**Système complet** (test + 20 % du contentieux du périmètre, 5 441 clients) : règle seule, 35,5 % des défauts, précision 70,5 % ; règle + haut risque (30 % de rappel), 55,1 %, précision 56,8 % ; règle + modèle au rappel minimal, 74,7 %, précision 39,5 %, 41,6 % des clients signalés. Mêmes taux par niveau sur tout le périmètre du ML (27 202 clients : 35,4 %, 54,9 %, 74,3 %). Ces niveaux sont ceux de l'évaluation, à quatre niveaux ; le découpage en cinq niveaux est décrit plus bas (borne de 10 %).

**Décision** : version finale confirmée sur le test, dans l'intervalle de la validation ; plafond attribué à la cible (`methodologie_ML.md`, section 13).

**Borne de 10 % ajoutée le 07/10/2026, après la lecture du test** : seuil qui détecte 10 % des défauts sur les probabilités hors pli du train (0,773), fixé comme les bornes de 30 % et 60 %, sans changement du modèle ni du seuil de décision ; elle coupe le haut risque en deux. Sur tout le périmètre du ML : très haut risque, 752 clients, 51,3 % de défaut ; haut risque, 2 057 clients, 37,7 % (test seul : 144 clients, 53,5 % ; 416 clients, 38,0 %). Choix d'une borne ronde, pas d'une borne cherchée pour garder la précision au-dessus de 50 %.

## 4. Notebooks hors scénarios

Ces notebooks n'écrivent rien dans le fichier de résultats et n'enregistrent aucun modèle : ils diagnostiquent, tranchent un point de méthode ou décrivent. Ordre pour les relancer : `methodologie_ML.md`, section 0. Hypothèses et conclusions qu'ils soutiennent : `docs/hypotheses_et_conclusions.md`.

| Notebook | But | Résultat | Décision |
|---|---|---|---|
| [`diagnostic_capacite`](diagnostic_capacite.ipynb) | La règle de surapprentissage bride-t-elle les modèles ? (modèles poussés sur les colonnes de `ml_11`) | Aucun réglage poussé ne dépasse `ml_11` : RandomForest profondeur 12 à égalité (0,489) ; CatBoost poussé -0,015 à -0,018 ; MLP sans arrêt anticipé -0,05 à -0,06 | Plateau attribué aux données ; règle de surapprentissage gardée (méthodologie, section 7) |
| [`diagnostic_encodage_pay`](diagnostic_encodage_pay.ipynb) | Encoder les `PAY_n` en catégories (à jour / 1 / 2 et plus) plutôt qu'en nombres | Dans le bruit pour tous les modèles | Encodage numérique de la v6 conservé |
| [`elagage_ml`](elagage_ml.ipynb) | Retirer les groupes de colonnes inutiles, à partir de `ml_11` | Seul le résumé des codifications est gardé ; démographie retirée ; perte cumulée -0,004, dans le bruit | Version élaguée reprise dans `ml_12` |
| [`duel_fin_ml14_ml15`](duel_fin_ml14_ml15.ipynb) | Trancher finement le duel `ml_15` contre `ml_14` (5 plis × 10 répétitions, test t corrigé de Nadeau et Bengio) | Meilleur contre meilleur +0,0026 ± 0,0063, 31 plis sur 50, t = 0,79, dans le bruit | `ml_14` reste la version de base |
| [`ml_16`](ml_16.ipynb) | Reprendre le groupe à population faible (traces des corrections, 0,7 % du train) avec la même mesure fine | Meilleur contre meilleur +0,0003, t = 0,33 ; régression logistique +0,0012, t = 1,24 ; dans le bruit | Groupe écarté définitivement (ligne de `ml_2`) ; version finale `ml_14` |
| [`analyse_defauts_manques`](analyse_defauts_manques.ipynb) | Qui sont les défauts qu'aucun modèle ne détecte ? (25 % du train, découpage fixé avant) | 248 défauts sur 771 manqués par les 4 modèles de `ml_14`, indiscernables des bons clients non signalés (8 indicateurs sur 9) | Une part de la cible est imprévisible avec ces données ; aucune colonne construite (méthodologie, section 13) |
| [`evaluation_finale_test`](evaluation_finale_test.ipynb) | Lire le test une seule fois | Section 3 de ce journal | Version finale confirmée |
| [`controles_cible`](controles_cible.ipynb) | Recalculer les chiffres sur la cible cités dans les hypothèses ; rejuger les scénarios sur la précision moyenne | Clients sans dette en défaut à 18,2 % ; contentieux qui paie en défaut à 70,7 % ; aucun scénario ne dépasse le socle `ml_0` en précision moyenne (`ml_14` : 0,334 contre 0,337, dans le bruit) | Descriptif : renvois dans les hypothèses |
| [`eda_population_ml`](eda_population_ml.ipynb) | Comprendre ce qui fait encore varier le défaut dans la population du ML (train seul), une fois retirés les clients en incident à M et en retard imminent | À lire après exécution | Descriptif : ne choisit aucune variable |
| [`comparatif_global/`](comparatif_global/) | Essais sur le jeu de base, le jeu corrigé, séparés ou non par la règle du contentieux ou la codification de la banque (test du ML inclus : diagnostic seulement) | Hors contentieux, les montants seuls font jeu égal avec `ml_4` ; au contentieux, aucun client ne peut être sorti ; la règle du contentieux fait jeu égal avec la codification de la banque ; toutes les approches sur la même courbe de niveaux de risque | Réponse partielle à la problématique ; aucun effet sur la version finale |

