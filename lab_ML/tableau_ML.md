# 📐 Journal des scénarios du machine learning

> Ce journal suit le machine learning actuel, redémarré après la définition de la population contentieuse. La première itération, entraînée sur le dataset **avec** la population contentieuse, est archivée dans [`1ere_iteration/`](1ere_iteration/) avec son propre journal ([`1ere_iteration/tableau_ML.md`](1ere_iteration/tableau_ML.md)) ; elle reste la référence de performance à battre.

## 1. Données

* **Source** : `data/csv_streamlit/dataset_streamlit.csv`, c'est-à-dire le dataset nettoyé `cleaned5` (niveaux 0 à 5 de `src/02_01_nettoyage.ipynb`) et les colonnes créées dans `src/05_03_EDA_storytelling.ipynb`.
* **Création des jeux** : [`creation_datasets_ML.ipynb`](creation_datasets_ML.ipynb), exécuté une seule fois, produit `data/ML/train_dataset.csv` et `data/ML/test_dataset.csv`.
  1. Périmètre : clients avec une dette en septembre (`BILL_AMT1 > 0`) et plafond de 500 000 NT$ ou moins. Règle métier : on cherche un risque réel.
  2. Retrait des clients au contentieux à M (`FLAG_CTX` = 1 et `MOIS_SORTIE_CTX` = -1), prédits en défaut par la règle métier.
  3. Découpage 80/20 des clients restants, stratifié sur `dpnm`, `random_state=42`.
* **Colonnes** : seules les 25 colonnes d'origine et les colonnes répertoriées dans [`docs/colonnes_creees.md`](../docs/colonnes_creees.md) entrent dans le ML ; un contrôle de `creation_datasets_ML.ipynb` bloque l'enregistrement sinon. Une nouvelle colonne se calcule client par client, dans ce notebook, avant le découpage.

## 2. Méthode commune à tous les scénarios

* **Train uniquement** : validation croisée stratifiée à 5 plis, `random_state=42`. Le jeu de test n'est lu qu'une seule fois, à la fin, sur le modèle figé.
* **Score de décision** : moyenne du F2 (au seuil de 0,5) et du ROC AUC, mesurés en validation. Il est le seul critère de choix d'un scénario ou d'un modèle.
* **Bruit** : le score de décision est donné avec son écart-type sur les 5 plis. Un gain plus petit que cet écart-type n'est pas retenu comme une amélioration.
* **Référence naïve** : prédire « défaut » pour tous les clients donne un rappel de 100 %, une précision égale au taux de défaut (environ 16 % sur le train), donc un F2 d'environ 0,49, et un ROC AUC de 0,50 : un score de décision d'environ 0,49 sans aucun modèle. Un score se lit par son écart à cette référence, et la précision par son écart au taux de défaut.
* **Défauts détectés et précision** : comptés en validation (chaque client est prédit par un modèle qui ne l'a pas vu), au seuil de 0,5. Le seuil sera réglé sur le modèle final.
* **Modèles** : les 6 modèles d'origine (LogisticRegression, SVM, MLPClassifier, KNN, RandomForest, CatBoost), optimisés par GridSearch sur le score de décision.
* **Surapprentissage** : alerte quand l'écart train - val du score de décision dépasse 0,05 (forte au-delà de 0,10). Les hyperparamètres sont cherchés par une boucle automatique de GridSearch (4 tours au plus par modèle) : à chaque tour, meilleur score de décision parmi les réglages sous le seuil de surapprentissage, puis grille corrigée (paramètre au bord : grille prolongée ; surapprentissage : paramètres poussés vers un modèle plus simple, dans des bornes fixées). Un modèle sort de la boucle quand il n'a plus ni surapprentissage ni paramètre au bord, quand le gain devient plus petit que l'écart-type, ou quand ses bornes sont atteintes ; le meilleur tour est gardé, sans réentraînement.
* **Un notebook par scénario** : `ml_0`, `ml_1`… Chaque scénario part du précédent retenu et ajoute un petit groupe de colonnes.

## 3. Scénarios

| Scénario | Ce qui change | Variables | Meilleur modèle | Score de décision (val) | Défauts détectés / précision (val) | Décision |
|---|---|---|---|---|---|---|
| [`ml_0`](ml_0.ipynb) | Socle : les 23 variables d'origine, sans colonne créée ; 6 modèles | 23 | CatBoost (⚠️ surapprentissage 0,068), à égalité avec RandomForest (0,5949 ± 0,0136, ✅ 0,037) | 0,5981 ± 0,0130 | CatBoost : 1 822 sur 3 084 (59,1 %) / 27,9 % ; RandomForest : 1 850 (60,0 %) / 26,9 % | Référence des scénarios suivants. Même trio de tête que la première itération (CatBoost, RandomForest, LogisticRegression). Résultats obtenus avec l'ajustement à la main, avant la boucle automatique : surapprentissage de CatBoost ramené de 0,106 à 0,068, RandomForest passé sous le seuil (0,051 à 0,037), scores inchangés dans le bruit. *À relancer avec la boucle.* KNN, SVM et MLP détectent presque aucun défaut au seuil de 0,5 |

## 4. Évaluation finale (une seule fois, sur le test)

*À faire quand le modèle sera figé.* Le système complet (la règle métier pour les clients au contentieux à M, le modèle pour les autres) sera comparé à la règle seule et à la première itération, en défauts détectés et en précision. Les modalités de la comparaison avec la première itération seront fixées à ce moment-là : son test n'est pas celui du ML actuel.
