# 📐 Journal des scénarios du machine learning

> Ce journal suit le machine learning actuel, redémarré après la définition de la population contentieuse. La première itération, entraînée sur le dataset **avec** la population contentieuse, est archivée dans [`1ere_iteration/`](1ere_iteration/) avec son propre journal ([`1ere_iteration/tableau_ML.md`](1ere_iteration/tableau_ML.md)) ; elle reste la référence de performance à battre.

## 1. Données et méthode

⚠️ **Après un clone du dépôt** : les fichiers produits par les lancements (train et test, probabilités hors pli, fichier de résultats, modèles) ne sont pas dans le dépôt. Les sorties des notebooks se lisent telles quelles, mais pour relancer ou comparer un scénario, il faut d'abord exécuter `creation_datasets_ML`, puis les scénarios précédents dans l'ordre : voir la section 0 de la méthodologie.

La méthode commune à tous les scénarios (données, étalon, validation, boucle d'optimisation, raisons d'arrêt, alertes, fichiers enregistrés, évaluation finale) est décrite dans [`methodologie_ML.md`](methodologie_ML.md). En bref :

* **Données** : périmètre S12 sans les clients au contentieux à M, découpage 80/20 propre au ML ([`creation_datasets_ML.ipynb`](creation_datasets_ML.ipynb)) ; le test n'est lu qu'une seule fois, à la toute fin du machine learning, une fois tous les scénarios faits et le modèle final figé (jamais dans un notebook de scénario).
* **Étalon** : la **précision des défauts prédits, au taux de rappel minimal** (60 % pour commencer, objectif 70 %), en validation croisée à 5 plis sur le train, avec son écart-type ; un gain plus petit que l'écart-type n'est pas retenu. Elle se compare au taux de défaut du train (environ 16 %), précision d'un tri au hasard.
* **Hyperparamètres** : boucle automatique de GridSearch, sous contrainte de surapprentissage, jusqu'à stabilisation du modèle.
* **Un notebook par scénario** : `ml_0`, `ml_1`… Chaque scénario part du précédent retenu et ajoute un petit groupe de colonnes.

## 2. Scénarios

| Scénario | Ce qui change | Variables | Étalon | Meilleur modèle | Scores (val) | Défauts détectés / précision (val) | Décision |
|---|---|---|---|---|---|---|---|
| [`ml_0_etalon`](ml_0_etalon.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles ; ajustement à la main (04/10/2026) | 23 | Moyenne du F2 au seuil de 0,5 et du ROC AUC (méthode v0) | CatBoost (⚠️ surapprentissage 0,068), à égalité avec RandomForest (0,5949 ± 0,0136, ✅ 0,037) | 0,5981 ± 0,0130 | CatBoost : 1 822 sur 3 084 (59,1 %) / 27,9 % ; RandomForest : 1 850 (60,0 %) / 26,9 % | Référence des scénarios suivants. Même trio de tête que la première itération (CatBoost, RandomForest, LogisticRegression). Résultats obtenus avec l'ajustement à la main, avant la boucle automatique : surapprentissage de CatBoost ramené de 0,106 à 0,068, RandomForest passé sous le seuil (0,051 à 0,037), scores inchangés dans le bruit. Point de départ de la méthode ; c'est ici que le rappel minimal de départ (60 %) a été constaté. KNN, SVM et MLP ne détectent presque aucun défaut au seuil de 0,5 |
| [`ml_0`](ml_0.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles | 23 | Précision à 60% de rappel (méthode v4) | CatBoost (écart relatif train - val 2,3 %), à égalité avec RandomForest, SVM | 26,8 % ± 1,8 pts (ROC AUC 0,702) | 1 851 sur 3 084 (60,0 %) / 26,5 %, 36,0 % des clients signalés | *à compléter* |
| [`ml_0`](ml_0.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles | 23 | Classement : score décisionnel F2 ; réglage : précision des défauts prédits (taux de rappel minimal 60%, méthode v5) | CatBoost (écart relatif train - val 2,3 %), à égalité avec RandomForest, SVM | score décisionnel F2 0,481 ± 0,011 ; précision 26,8 % ± 1,8 pts ; ROC AUC 0,702 | 1 851 sur 3 084 (60,0 %) / 26,5 %, 36,0 % des clients signalés | *à compléter* |
| [`ml_0`](ml_0.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles | 23 | Classement : score décisionnel F2 ; réglage : précision des défauts prédits (taux de rappel minimal 60%, méthode v6) | CatBoost (écart relatif train - val 4,6 %), à égalité avec RandomForest, KNN, SVM | score décisionnel F2 0,481 ± 0,012 ; précision 26,9 % ± 1,8 pts ; ROC AUC 0,708 | 1 851 sur 3 084 (60,0 %) / 26,6 %, 35,9 % des clients signalés | *à compléter* |

## 3. Évaluation finale (une seule fois, sur le test)

*À faire quand le modèle sera figé.* Le système complet (la règle métier pour les clients au contentieux à M, le modèle pour les autres) sera comparé à la règle seule et à la première itération, en défauts détectés et en précision. Les modalités de la comparaison avec la première itération seront fixées à ce moment-là : son test n'est pas celui du ML actuel.
