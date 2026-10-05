# 🧭 Méthodologie du machine learning

> Méthode commune à tous les scénarios (`ml_0`, `ml_1`…). Les résultats de chaque scénario sont consignés dans [`tableau_ML.md`](tableau_ML.md). Toute évolution de la méthode est datée dans la section 11.

## 0. Reproduire le machine learning après un clone du dépôt

Le dépôt contient les notebooks avec leurs sorties et ce document. Les données brutes ne sont pas dans le dépôt : elles se téléchargent (lien dans le README) et se placent dans `data/raw/`, sous le nom `default of credit card clients.csv`. **Il ne contient pas les fichiers produits par les lancements** (ignorés par git) : les jeux d'entraînement et de test (`data/ML/train_dataset.csv`, `test_dataset.csv`), les probabilités hors pli (`data/ML/probas_hors_pli/`), le fichier de résultats (`data/ML/resultats_scenarios.csv`) et les modèles enregistrés (`lab_ML/best_models/`).

Après un clone, les sorties des notebooks se lisent telles quelles, mais **rien ne se compare ni ne se relance sans régénérer ces fichiers**, dans l'ordre :
1. exécuter `src/02_01_nettoyage.ipynb` **en entier**, jusqu'au niveau de nettoyage le plus élevé (`cleaned5_creditcard.csv` aujourd'hui) ; **pour nous aussi** : après toute correction de nettoyage, on repart de là ;
2. exécuter `creation_datasets_ML.ipynb` : il part du fichier du niveau de nettoyage le plus élevé, sans dépendre de l'EDA ni de Streamlit, et recrée le train et le test à l'identique (clients triés par `ID`, graine fixée) ;
3. exécuter `ml_0`, puis chaque scénario **dans l'ordre**, jusqu'à celui qui nous intéresse : chaque scénario a besoin des fichiers du scénario auquel il se compare (sa référence, cellule 1), et les comparaisons libres de ceux qu'elles citent ;
4. avec la même version de la méthode que celle des sorties consultées : un scénario relancé avec une autre version ne se compare pas aux autres.

Les graines étant fixées, les scores obtenus sont les mêmes que ceux des sorties enregistrées (aux différences près entre versions de bibliothèques). Le temps de calcul dépend fortement de la machine (les calculs sont répartis sur tous les cœurs du processeur) et s'allonge d'un scénario à l'autre : le socle `ml_0` est le plus léger, chaque scénario suivant ajoute des variables. `ml_0_etalon.ipynb` (archive de la méthode v0) se lit sans être relancé : il n'écrit aucun fichier utilisé par les autres.

## 1. Données et découpage

* **Source** : le fichier du **niveau de nettoyage le plus élevé** produit par `src/02_01_nettoyage.ipynb` (`data/cleaned5_creditcard.csv` aujourd'hui : niveaux 0 à 5, codifications corrigées et colonnes du contentieux), choisi automatiquement ; les clients sont triés par `ID` avant le découpage. Le ML ne dépend ni de l'EDA ni du dataset de Streamlit (depuis le 05/10/2026 ; le découpage obtenu est identique à celui d'avant).
* **Création des jeux** : [`creation_datasets_ML.ipynb`](creation_datasets_ML.ipynb) produit `data/ML/train_dataset.csv` et `data/ML/test_dataset.csv` :
  1. périmètre : clients avec une dette en septembre (`BILL_AMT1 > 0`) et plafond de 500 000 NT$ ou moins ;
  2. retrait des clients au contentieux à M (`FLAG_CTX` = 1 et `MOIS_SORTIE_CTX` = -1) : ils sont prédits en défaut par la règle métier, le machine learning travaille sur les autres ;
  3. découpage 80/20 des clients restants, stratifié sur `dpnm`, `random_state=42`.
* **Colonnes** : seules les 25 colonnes d'origine et les colonnes répertoriées dans [`docs/colonnes_creees.md`](../docs/colonnes_creees.md) entrent dans le ML. Une nouvelle colonne se calcule client par client, dans `creation_datasets_ML.ipynb`, avant le découpage, **au moment où un scénario en a besoin**. Un contrôle compare chaque colonne présente aussi dans le dataset de Streamlit, client par client : un écart bloque l'enregistrement (une seule définition, jamais deux résultats).
* **Source tracée** : `data/ML/source_datasets.json` (fichier et niveau de nettoyage, dates), recopiée dans le fichier de résultats.
* **Le test n'est lu qu'une seule fois**, à la toute fin du machine learning, une fois tous les scénarios faits et le modèle final figé (jamais dans un notebook de scénario) (section 10).

## 2. Objectif et étalon : la précision des défauts prédits, au taux de rappel minimal

* **Rappel minimal** (`RAPPEL_MINIMAL`) : la part des défauts que le modèle doit trouver. **60 % pour commencer, objectif 70 %.**
* **D'où viennent les 60 %** : une première passe de `ml_0`, avec l'ancien score (voir plus bas), ne contenait pas ce critère. Les meilleurs modèles y trouvaient déjà environ 60 % des défauts, sans être réglés pour ça. On part de ce niveau atteint, puis on vise 70 %. Ces résultats initiaux sont conservés dans [`ml_0_etalon.ipynb`](ml_0_etalon.ipynb) (archive du 04/10/2026, ajustement à la main, à ne pas réexécuter pour garder ses sorties ; son modèle s'enregistrerait sous `model_ml_0_etalon.joblib`). C'est un constat de départ, pas une valeur optimisée sur `dpnm`.
* **La boucle optimise la précision des défauts prédits** : la part des clients prédits en défaut qui font réellement défaut, mesurée au seuil qui atteint le taux de rappel minimal. Sur chaque pli de validation :
  1. les clients sont rangés de la probabilité de défaut la plus haute à la plus basse ;
  2. le seuil est placé là où le modèle a trouvé la part voulue des défauts (fonction `seuil_pour_rappel`) ;
  3. la précision est la part des clients signalés qui sont réellement en défaut.

  Le seuil n'est pas optimisé : il découle du rappel minimal. Tous les modèles sont jugés au même rappel, quel que soit le niveau de leurs probabilités.
* **Qui fait quoi : le seuil et les hyperparamètres**

  | | Rôle | Comment il est fixé |
  |---|---|---|
  | Seuil | atteindre le rappel minimal | **calculé, pas optimisé** : pour un modèle donné, un seul seuil donne ce rappel ; il est propre à chaque modèle (il n'est plus fixé à 0,5) |
  | Hyperparamètres | donner la meilleure précision à ce rappel | **optimisés** par la boucle (section 5) |

  La précision se gagne par la qualité du **tri** des clients : un meilleur modèle place plus de vrais défauts en tête de liste, atteint donc le rappel minimal en signalant moins de clients, et fait moins de fausses alertes. Ce tri s'améliore par les hyperparamètres (la boucle) puis par les nouvelles variables (les scénarios), jamais en déplaçant le seuil.
* **Le seul levier sur le seuil est le rappel minimal** : le monter baisse le seuil de chaque modèle (plus de défauts trouvés, plus de clients signalés). C'est une décision métier (voir « Monter la cible » plus bas), pas une optimisation.
* **Rappel minimal** : le seuil est le plus haut qui détecte **au moins** le rappel visé. Un modèle qui ne sait pas s'arrêter pile (probabilités à égalité, comme le KNN) le dépasse un peu : on le mesure à son vrai point de fonctionnement, sans tronquer ses prédictions.
* **Score de classement final : le « score décisionnel F2 »** (depuis la v5). Il n'entre pas dans l'apprentissage : la boucle choisit les réglages sur la précision au rappel minimal. Une fois les modèles retenus, le F2 de chacun est calculé **à la fin, à son propre rappel** (celui qu'il atteint à son seuil, au moins 60 %) **et à sa propre précision**, pli par pli, avec son écart-type. Il sert à **classer les modèles** (podium, modèle enregistré) et à **comparer les scénarios**. Il monte avec la précision et avec le rappel : à rappel égal, la précision gagne ; à précision égale, le rappel gagne ; il départage donc aussi un modèle qui dépasse un peu le rappel minimal. Les autres métriques restent calculées, affichées et enregistrées.
* **Pourquoi la boucle ne surveille pas le F2** : à rappel fixé, le F2 ne bouge qu'environ un tiers autant que la précision ; les seuils de surapprentissage, de plancher et d'instabilité, calibrés sur la précision, deviendraient environ trois fois plus tolérants. Exemple : le CatBoost de la v3 a un écart relatif de 15,5 % sur la précision (surapprentissage), mais de 4,9 % sur le F2 (il passerait pour sain). Le F2 n'est donc qu'un calcul final de classement.
* **Contrôles affichés** : le ROC AUC (qualité du tri des clients, sans seuil) et la précision moyenne (précision moyenne sur tous les rappels).
* **Lecture** : une précision se compare au taux de défaut du train (environ 16 %), qui est la précision d'un tri au hasard, quel que soit le rappel. Une précision n'a de sens qu'avec le rappel auquel elle est mesurée : deux précisions mesurées à des rappels différents ne se comparent pas.
* **Pourquoi pas le seuil de 0,5 ni le F2** : l'ancien score était la moyenne du F2 au seuil de 0,5 et du ROC AUC.
  * Le seuil de 0,5 pénalisait les modèles dont les probabilités restent basses (SVM calibré, KNN et MLP sans pondération des défauts). Ils triaient presque aussi bien que les meilleurs, mais ne détectaient presque aucun défaut à 0,5.
  * Le seuil qui maximise le F2 poussait à signaler une majorité des clients, ce qu'aucune banque ne peut suivre.
* **Monter la cible** (vers 70 %, voire plus) : pour un modèle donné, plus de rappel veut dire moins de précision. C'est un arbitrage métier (plus de défauts trouvés, mais plus de fausses alertes), décidé au vu du volume d'alertes acceptable. On n'essaie pas plusieurs cibles pour garder la plus flatteuse, et le test ne sert jamais à choisir la cible.
* **Pas de comparaison de rappel avec la règle du contentieux** : la règle isole une population qui n'est plus en gestion standard ; elle ne vise ni un rappel ni une précision.
* **Point connu** : quand beaucoup de clients ont la même probabilité (KNN, dont les probabilités ne prennent que quelques dizaines de valeurs), le seuil ne peut pas couper au milieu de ce groupe : le rappel mesuré dépasse un peu la cible, et la précision est un peu sous-estimée.

## 3. Validation croisée et bruit

* Validation croisée stratifiée à 5 plis, `random_state=42`, sur le train uniquement.
* La précision est donnée avec son **écart-type sur les 5 plis**. Un écart entre deux modèles, ou un gain d'un tour à l'autre, plus petit que cet écart-type est du bruit : les deux sont à égalité.
* **Limite connue : le hasard interne des modèles.** La comparaison pli par pli mesure le bruit dû au découpage des clients, pas celui dû au hasard interne de RandomForest, CatBoost et du MLP (graine, ordre des colonnes). Mesuré sur le socle : la seule graine fait varier le score décisionnel F2 de RandomForest d'environ 0,002 à 0,003. Pour ces trois modèles, un gain ou une perte de cet ordre n'est pas une preuve, même si le verdict dit « réel » ; le KNN, le SVM et la régression logistique n'ont pas de hasard interne, leurs écarts sont fiables. La référence elle-même peut être bien ou mal tombée : on lit donc les petits écarts des modèles aléatoires avec prudence.
* Plus on teste de réglages, plus le score de validation devient optimiste (un réglage peut avoir eu de la chance sur ces 5 plis). Le test, lu une seule fois à la toute fin du machine learning, reste le vrai juge.

## 4. Modèles, variables et encodage

* **Modèles** : les 6 modèles d'origine (LogisticRegression, SVM, MLPClassifier, KNN, RandomForest, CatBoost), choisis dans `MODELES_A_TESTER`. Pour gagner du temps de calcul, un modèle peut être retiré des scénarios suivants quand son retard sur le premier est confirmé sur deux scénarios (écart plus grand que l'écart-type).
* **Le MLP reste dans tous les scénarios**, quel que soit son rang : dans l'étude de Yeh et Lien (2009), c'est le réseau de neurones qui obtient les meilleurs résultats. Le garder permet de comparer notre démarche à la leur, à type de modèle égal.
* **Variables** : une seule cellule à modifier par scénario (« variables du scénario »), avec `ajout_num` (nombres, ratios, compteurs, indicateurs, et toute variable déjà numérique et ordonnée), `ajout_cat` (catégories sans ordre), `ajout_ord` (catégories ordonnées qui ne sont pas des nombres) et `retirees` (colonnes du socle retirées). Le socle est formé des 23 variables d'origine ; `ID` et `dpnm` ne sont jamais des variables.
* **Encodage**, dans le pipeline (appris sur chaque pli, sans fuite) : `StandardScaler` pour les nombres, **`PAY_1` à `PAY_6` compris** (depuis la v6) ; `OneHotEncoder` pour les catégories sans ordre ; `OrdinalEncoder` suivi d'un `StandardScaler` pour les catégories ordonnées qui ne sont pas des nombres (aucune dans le socle).
  * **`StandardScaler`** : moyenne 0 et écart-type 1 pour chaque variable, sans bornes (les valeurs extrêmes restent extrêmes) ; l'ordre et les écarts entre valeurs sont gardés. Il donne à chaque variable le même étalement, donc les mêmes chances au départ dans les modèles qui calculent des distances ou des poids (KNN, SVM, MLP, régression logistique) ; les arbres (CatBoost, RandomForest) n'en dépendent pas.
  * **Pourquoi les `PAY_n` ne passent plus par l'`OrdinalEncoder` (v6)** : leurs valeurs (-2 à 8) sont déjà ordonnées et régulièrement espacées. L'`OrdinalEncoder` les remplaçait par leur rang parmi les valeurs vues à l'entraînement de chaque pli ; une valeur absente de l'entraînement (retard rare de 6, 7 ou 8 mois, porté par des clients sortis du contentieux : 351 clients du ML ont au moins un `PAY_n` > 2) était encodée -1, **sous** les meilleurs payeurs. Constaté 4 fois sur les 5 plis. Traités comme des nombres, un retard de 8 mois reste le plus grand. L'hypothèse d'ordre (-2, -1, 0, puis les retards) est la même qu'avant.
* **Déséquilibre des classes** : pondération des défauts quand le modèle l'accepte (`class_weight='balanced'`, `scale_pos_weight` pour CatBoost). KNN et MLP n'ont pas cette option. Avec la précision au rappel minimal, ils ne sont plus pénalisés pour autant : seul compte leur tri.

## 5. Recherche des hyperparamètres : une boucle automatique

Dans la première itération, les grilles étaient retouchées et le surapprentissage jugulé à la main, scénario par scénario. La recherche est désormais **automatique et reproductible** : une boucle de GridSearch, en tours successifs, pour chaque modèle.

1. **GridSearch** sur la grille du tour. Le premier tour part des grilles de la première itération.
2. **Choix sous contrainte** : parmi les réglages qui **battent le hasard** (précision au-dessus du taux de défaut d'au moins un écart-type), ceux dont l'écart relatif train - val du score reste sous le seuil de surapprentissage (section 7), celui qui a le meilleur score en validation ; si aucun ne passe, celui qui surapprend le moins.
3. **Correction de la grille** pour le tour suivant :
   * paramètre **au bord** de sa grille (la meilleure valeur est la plus petite ou la plus grande testée) : la grille est prolongée de ce côté ;
   * **surapprentissage** : chaque paramètre numérique est poussé dans le sens qui simplifie le modèle (arbres moins profonds, feuilles plus grosses, régularisation plus forte, apprentissage plus lent…) ;
   * les autres paramètres sont fixés à leur meilleure valeur, pour que la grille reste petite ;
   * chaque paramètre reste dans des bornes fixées à l'avance, avec un pas fixé (tableau `REGLAGES_PARAMETRES`) ;
   * les paramètres non numériques (`gamma`, `weights`, architecture du MLP) et le nombre d'arbres du RandomForest sont choisis au premier tour, puis fixés ;
   * le nombre d'arbres de CatBoost (`iterations`) part de 1 000, sa valeur par défaut, et n'est réduit qu'en cas de surapprentissage (ajouté le 05/10/2026).
4. **Version retenue** : choisie parmi tous les tours joués. D'abord les tours qui battent le hasard et sans surapprentissage ; parmi eux, ceux à moins d'un écart-type du **meilleur score de tous les tours** ; et parmi ces derniers, celui qui surapprend le moins. On compare toujours au meilleur score, jamais au seul tour précédent : sinon, de petites pertes « dans le bruit » à chaque tour s'additionnent. La version retenue est déjà entraînée sur tout le train par la GridSearch : pas de réentraînement.

Un modèle arrêté sort de la boucle et n'est plus relancé.

**CatBoost et la taille des feuilles** : CatBoost construit par défaut des arbres symétriques (tous les clients d'un même niveau passent par la même question), déjà très contraints. Avec cette forme d'arbre, `min_data_in_leaf` (taille minimale d'une feuille) est ignoré sans message : vérifié le 05/10/2026 sur le train, il ne change aucune probabilité ; dans la première itération, il n'avait donc aucun effet. Il n'agit qu'avec `grow_policy='Depthwise'` (chaque branche choisit sa propre question, comme un arbre classique), qui est un autre modèle, plus souple. **Piste** : tester cette variante seulement si CatBoost est encore dans le top 3 avec les variables finales.

**Limites** : la recherche est locale. Elle avance pas à pas autour du meilleur réglage, n'affine pas entre deux valeurs testées quand la meilleure est à l'intérieur de la grille, ne teste jamais un paramètre absent de la grille de départ, et ne rouvre pas un paramètre fixé.

## 6. Raisons d'arrêt

Il n'y a pas de nombre de tours fixé : la boucle tourne jusqu'à ce que le modèle se stabilise. La première condition remplie l'emporte.

| Raison de l'arrêt | Quand |
|---|---|
| sous-apprentissage : le réglage choisi ne bat plus le hasard | sa précision ne dépasse plus le taux de défaut d'au moins un écart-type : simplifier davantage n'a plus de sens ; le meilleur tour précédent est gardé |
| optimisé : ni surapprentissage ni paramètre au bord | le réglage choisi est sous le seuil de surapprentissage et à l'intérieur de sa grille |
| convergé : le réglage choisi ne change plus | même réglage qu'au tour précédent |
| stagnation : gain plus petit que l'écart-type, entre deux tours sans surapprentissage | le gain est dans le bruit ; un tour qui corrige un surapprentissage perd souvent un peu de score, ce n'est pas compté comme une stagnation |
| bornes atteintes : la grille ne peut plus bouger | aucun paramètre ne peut plus avancer dans ses bornes |
| convergé : la grille suivante ne contient aucun réglage nouveau | toutes les combinaisons prévues ont déjà été testées |
| ⚠️ garde-fou atteint : grilles ou bornes à revoir | `TOURS_SECURITE` tours (15) joués sans stabilisation ; ne doit pas arriver |

## 7. Seuils de surapprentissage et d'instabilité

Le surapprentissage se mesure par l'**écart relatif** : l'écart train - val du score divisé par le score de validation, c'est-à-dire la part du score que le modèle perd hors des clients d'entraînement. Il garde le même sens quel que soit le niveau du score ou l'étalon. Les écarts en points (pts) sont affichés à côté (0,05 = 5 points de précision).

| Alerte | Seuil | Rôle |
|---|---|---|
| ⚠️ SURAPPRENTISSAGE | écart relatif train - val au-delà de 5 % (`SEUIL_SURAPPRENTISSAGE`) | **contrainte et motif de réoptimisation** : un réglage au-delà n'est retenu que si aucun autre ne passe, et le modèle est simplifié au tour suivant (section 5) |
| ⚠️⚠️ SURAPPRENTISSAGE FORT | écart relatif au-delà de 10 % | même rôle, signalé plus fortement |
| ⚠️ N'APPREND RIEN | précision en validation pas plus haute que le taux de défaut + un écart-type | **plancher** : le réglage est écarté du choix, et la boucle s'arrête si le réglage choisi y tombe |
| ⚠️ INSTABLE | écart-type du score sur les plis au-delà de 2 pts (`SEUIL_INSTABILITE`) | **alerte seule** : ne déclenche aucune réoptimisation |

* **Pourquoi l'instabilité n'est pas une contrainte** : un écart-type mesuré sur 5 plis est lui-même trop incertain pour décider seul d'un réglage ; et l'instabilité du MLP vient surtout du hasard de son initialisation, que la grille corrige mal.
* **Pourquoi en relatif** : l'ancien seuil était de 0,05 en valeur absolue, sur un score d'environ 0,60 (environ 8 % du score). Sur une précision d'environ 0,27, ces 5 points représentaient environ 18 % du score : le seuil était devenu plus de deux fois plus tolérant. Le seuil relatif de 5 % est plus sévère que l'ancien (environ 1,4 point sur une précision de 27 %).
* **Limite connue** : l'écart relatif ne tient pas compte du niveau du hasard (16 % de précision, le taux de défaut). Le rapporter au gain sur le hasard serait plus rigoureux, mais plus difficile à expliquer pour un bénéfice faible.

## 8. Ce qui est enregistré et affiché

* **Matrices de confusion** au seuil du rappel minimal, et tableau de détection (seuil, clients signalés, défauts détectés, fausses alertes, défauts manqués, précision, rappel, part des clients signalés).
* **Précision et part des clients signalés à plusieurs rappels** (44, 60, 70 et 80 %). Le rappel de 44 % est celui de la première itération sur la population laissée au ML : point de comparaison indicatif (validation ici, test là-bas, découpages différents). Ces chiffres éclairent le choix du rappel minimal, ils ne le remplacent pas.
* **Probabilités hors pli** : `data/ML/probas_hors_pli/ml_<scénario>_<version>.csv` (`ID`, `dpnm`, version de la méthode, une colonne par modèle ; un fichier par scénario et par version, jamais écrasé par une autre version). Chaque client y est prédit par un modèle qui ne l'a pas vu. Toute métrique (autre rappel minimal, autre seuil, ancien score) se recalcule à partir de ce fichier, sans relancer les modèles. Réserve : les hyperparamètres restent ceux choisis pour l'étalon en vigueur lors du lancement.
* **Fichier de résultats** : `data/ML/resultats_scenarios.csv`, commun à tous les scénarios, une ligne par modèle (scénario, version de la méthode, date, **traçabilité** depuis la v6 : commit git du code, marqué « + modifications » si le code n'était pas commité, empreinte du fichier `train_dataset.csv`, niveau de nettoyage ; étalon, variables, scores, écarts, alerte, boucle, détection au rappel minimal). Relancer un scénario remplace ses lignes pour la même version de la méthode et garde celles des versions précédentes : le fichier trace l'effet de chaque évolution de la méthode. Il sert aux comparaisons entre scénarios et aux graphiques.
* **Comparaison avec le scénario de référence** (`scenario_reference`, choisi à la main : le scénario retenu, pas forcément le précédent) : le score décisionnel F2 est comparé **pli par pli** (même train, mêmes plis), pour le meilleur modèle de chaque scénario et pour chaque modèle présent dans les deux. Verdict : « gain réel » si le gain moyen dépasse l'écart-type des gains sur les plis, « perte » s'il est en dessous de moins cet écart-type, sinon « dans le bruit ». Les données viennent **uniquement des fichiers enregistrés** (probabilités hors pli, fichier de résultats) : aucun modèle n'est réentraîné, et la comparaison fonctionne après une réinitialisation du noyau. Elle est refusée si les deux scénarios n'ont pas la même version de la méthode ou le même rappel minimal.
* **Comparaisons libres** (section 8 du notebook) : la même comparaison entre deux scénarios quelconques (fusion de deux scénarios, contrôle par rapport au socle…), relancée seule autant de fois que voulu.
* **Ligne du journal** : chaque scénario affiche la ligne à recopier telle quelle dans `tableau_ML.md` (colonne « Décision » à compléter).
* **Meilleur modèle** : `lab_ML/best_models/model_ml_n.joblib` (premier du podium), **enregistré avec son seuil**. Le fichier est un dictionnaire : `modele`, `nom`, `seuil` (calculé sur les probabilités hors pli du train pour atteindre le rappel minimal), `rappel_minimal`, `variables` (colonnes attendues, dans l'ordre) et `scenario`. La méthode `predict()` du modèle coupe toujours à 0,5 : pour prédire, on compare `predict_proba(X)[:, 1]` au seuil enregistré.

## 9. Variables : on ajoute d'abord, on élague après le dernier scénario d'ajout

* **Ajout progressif** : chaque scénario `ml_n` part du scénario retenu choisi comme référence et ajoute un petit groupe de colonnes, gardé seulement si la comparaison pli par pli conclut à un **gain réel**.
* **D'où viennent les variables testées** : en grande partie de l'exploration déjà réalisée, qui les a construites et en a montré le lien avec le risque (toutes définies dans [`docs/colonnes_creees.md`](../docs/colonnes_creees.md)) : utilisation du plafond (`ratio_BILL_LIMITn`), ratios de paiement et type d'usage de la carte (`ratio_PAY_BILLn`, `ratio_PAY_BILL_global`, `ratio_PAY_BILL_median`, `TYPE_USAGE`, `ratio_PAY_BILL_regularite`), codification habituelle (`PAY_habituel_hors_retard`), vie du compte (`FLAG_OUVERTURE`, `FLAG_DEGEL`, `MOIS_ACTIVATION`), historique des retards et du contentieux (`CUMUL_INCIDENT`, `FLAG_RETARD`, `MOIS_SORTIE_RETARD`, `NB_MOIS_CTX`…). D'autres variables peuvent être créées si les résultats le suggèrent ; toute nouvelle variable est d'abord définie dans `docs/colonnes_creees.md`, puis calculée client par client dans `creation_datasets_ML.ipynb`, avant le découpage. Une variable peu utile seule peut le devenir avec une autre : on ne supprime pas en cours de route.
* **Importance des variables affichée** : un simple diagnostic, et un **contrôle de fuite**. Si une colonne pèse soudain beaucoup plus que les autres, on vérifie qu'elle n'utilise aucune information postérieure à septembre, aucun calcul sur l'ensemble des clients (médiane, quantiles) et aucun seuil choisi en regardant la cible. Cette importance n'est pas fiable pour élaguer (mesurée sur l'entraînement pour les arbres ; coefficients insensibles à la taille des catégories pour la régression logistique).
* **Élagage, après le dernier scénario d'ajout** (et avant la lecture du test) : retrait des variables une à une, ou par groupe, en gardant chaque retrait qui ne dégrade pas le score au-delà de l'écart-type. L'importance se mesure alors par permutation, sur les plis de validation, avec le précision.

## 10. Évaluation finale (une seule fois, sur le test, à la toute fin du machine learning)

* Le modèle est figé ; son seuil est fixé sur les probabilités hors pli du train pour atteindre le rappel minimal. Sur le test, le rappel tournera autour de la cible, sans la garantir exactement.
* Le système complet (la règle métier pour les clients au contentieux à M, le modèle pour les autres) est comparé à la règle seule et à la première itération, en défauts détectés et en précision. Les modalités de la comparaison avec la première itération seront fixées à ce moment-là : son test n'est pas celui du ML actuel.

## 11. Historique des changements de méthode

**Versions de la méthode** (`VERSION_METHODE` dans le notebook, colonne `version_methode` du fichier de résultats) :
* **v0** (04/10/2026) : GridSearch puis ajustement à la main ; score = moyenne du F2 au seuil de 0,5 et du ROC AUC (archive [`ml_0_etalon.ipynb`](ml_0_etalon.ipynb)) ;
* **v1** (05/10/2026) : boucle automatique, même score ;
* **v2** (05/10/2026) : score = précision au rappel minimal (60 %) ;
* **v3** (05/10/2026) : nombre d'arbres de CatBoost réglable par la boucle ;
* **v4** (05/10/2026) : seuil de surapprentissage relatif (5 %), plancher « bat le hasard », version retenue comparée au meilleur score de tous les tours.
* **v5** (05/10/2026) : classement final des modèles et comparaison des scénarios par le score décisionnel F2, calculé pour chaque modèle à son propre rappel (la boucle est inchangée).
* **v6** (05/10/2026) : `PAY_1` à `PAY_6` traités comme des nombres et mis à l'échelle (`StandardScaler`), au lieu de l'encodage ordinal ; traçabilité (commit, empreinte des données, niveau de nettoyage) dans le fichier de résultats. Données : le train et le test sont créés à partir du nettoyage le plus avancé, sans l'EDA (découpage identique).

Les changements sans effet sur les scores (alerte d'instabilité, seuil enregistré avec le modèle, affichage) ne créent pas de version.

**Effet mesuré de chaque version**, sur le socle `ml_0` (validation croisée sur le train ; meilleur modèle : CatBoost à chaque version). La précision à 60 % de rappel et le ROC AUC sont mesurés de la même façon pour toutes les versions : ce sont les mesures communes. À partir de la v4, le détail par modèle est dans `data/ML/resultats_scenarios.csv`.

| Version | Précision des défauts prédits (taux de rappel minimal 60 %) | ROC AUC | Écart train - val du meilleur modèle | Modèles en surapprentissage, au seuil de 5 % relatif | Modèles qui ne détectent presque aucun défaut au point de décision | Ce qui est vérifié |
|---|---|---|---|---|---|---|
| v0 | 27,5 % ± 1,0 (recalculée) | 0,713 | 0,068 sur l'ancien score (11 % relatif) | (non mesuré) ; au seuil de l'époque : CatBoost ⚠️, KNN ⚠️⚠️ | 3 sur 6 (SVM, KNN, MLP : moins de 8 % des défauts au seuil de 0,5) | point de départ |
| v1 | 27,4 % (sur l'ensemble du train) | 0,714 | 0,044 sur l'ancien score (7 % relatif) | (non mesuré) ; au seuil de l'époque : aucun | 3 sur 6 | la boucle corrige le surapprentissage sans perte de score, sans intervention |
| v2 | 27,7 % ± 1,2 | 0,713 | 4,2 pts (15 % relatif) | 5 sur 6 | aucun | SVM, KNN et MLP détectent de nouveau des défauts ; le SVM monte sur le podium |
| v3 | 27,8 % ± 1,5 | 0,714 | 4,3 pts (15 % relatif) | 5 sur 6 | aucun | même performance avec un CatBoost plus léger (445 arbres au lieu de 1 000) |
| v4 | 26,8 % ± 1,8 | 0,702 | 0,6 pt (2 % relatif) | aucun | aucun | plus aucun surapprentissage, pour une perte de 1 point de précision, dans le bruit ; trio de tête à égalité (CatBoost, RandomForest, SVM) |
| v5 | 26,8 % ± 1,8 (score décisionnel F2 : 0,481 ± 0,011) | 0,702 | 0,6 pt (2 % relatif) | aucun | aucun | mêmes modèles qu'en v4 (la boucle ne change pas) : même podium et mêmes égalités ; le score décisionnel F2 départage le KNN du MLP, à précision égale, grâce à son rappel un peu plus haut |
| v6 | 26,9 % ± 1,8 (score décisionnel F2 : 0,481 ± 0,012) | 0,708 | 1,2 pt (5 % relatif, sous le seuil) | aucun | aucun | erreur de logique corrigée (retards rares inconnus d'un pli) ; comparé à la v5 pli par pli : gain réel pour le KNN (+0,005 de score décisionnel F2, 4 plis sur 5 ; modèle sans hasard interne, gain fiable), les autres dans le bruit ; la « perte » de RandomForest (-0,002) n'est que du hasard (l'ordre des colonnes a changé, comme un changement de graine : sa seule graine fait varier son score de 0,478 à 0,481) ; quatre modèles à égalité en tête (CatBoost, RandomForest, KNN, SVM) |

Lecture : de la v0 à la v3, la performance ne bouge pas (dans le bruit), mais la méthode devient automatique (v1) et juge tous les modèles au même rappel (v2) ; le seuil absolu de 0,05 laissait pourtant 5 modèles sur 6 surapprendre d'environ 15 % en relatif. La v4 supprime ce surapprentissage pour un coût dans le bruit : les modèles apprennent une logique plutôt que le dataset.

| Date | Changement | Raison |
|---|---|---|
| 04/10/2026 | Redémarrage du ML sans le contentieux à M, découpage propre au ML, socle `ml_0`, un notebook par scénario | La population contentieuse est prédite par la règle métier |
| 05/10/2026 | Boucle automatique sans nombre de tours fixé, arrêt à la stabilisation | Remplacer l'ajustement à la main par une méthode reproductible |
| 05/10/2026 | Stagnation comptée seulement entre deux tours sans surapprentissage | Un tour qui corrige un surapprentissage arrêtait la recherche à tort |
| 05/10/2026 | Score optimisé par la boucle : précision au rappel minimal (60 %), au lieu de la moyenne du F2 au seuil de 0,5 et du ROC AUC | Le seuil de 0,5 masquait des modèles qui triaient bien ; le F2 poussait à signaler une majorité des clients |
| 05/10/2026 | Alerte d'instabilité (écart-type au-delà de 2 pts) | Repérer un modèle dont le score dépend trop des plis |
| 05/10/2026 | Probabilités hors pli enregistrées pour chaque scénario | Pouvoir changer d'étalon sans relancer les modèles |
| 05/10/2026 | Nombre d'arbres de CatBoost (`iterations`) réglable par la boucle | Levier contre le surapprentissage avec les arbres symétriques ; `min_data_in_leaf` y est sans effet |
| 05/10/2026 | Seuil enregistré avec le modèle | `predict()` coupe à 0,5 : le modèle seul ne reproduisait pas la détection mesurée |
| 05/10/2026 | Seuil de surapprentissage relatif : 5 % du score de validation (10 % pour l'alerte forte), au lieu de 0,05 en valeur absolue | Avec une précision d'environ 27 %, 5 points représentaient environ 18 % du score : le seuil absolu était devenu trop tolérant |
| 05/10/2026 | Plancher « bat le hasard » : un réglage doit dépasser le taux de défaut d'au moins un écart-type | Avec le seuil relatif strict, la boucle simplifiait un modèle jusqu'à ce qu'il n'apprenne plus rien (précision du hasard), et ce modèle vide l'emportait faute de surapprentissage |
| 05/10/2026 | Version retenue comparée au meilleur score de tous les tours, et non au tour précédent | Des égalités « dans le bruit » enchaînées tour après tour faisaient perdre du score de proche en proche |
| 05/10/2026 | Classement final par le score décisionnel F2, calculé pour chaque modèle à son propre rappel, pli par pli ; la boucle garde la précision | Un score unique qui réunit précision et rappel pour classer les modèles et comparer les scénarios, y compris quand un modèle dépasse un peu le rappel minimal |
| 05/10/2026 | Vocabulaire : « précision des défauts prédits » (le score optimisé par la boucle, mesuré au rappel propre à chaque modèle) et « score décisionnel F2 » (classement) remplacent « score de décision » et « F2 final » | Un nom par rôle, sans confusion avec le taux de rappel minimal ; pas de nouvelle version (les calculs ne changent pas) |
| 05/10/2026 | v6 : `PAY_n` traités comme des nombres et mis à l'échelle | Audit : l'encodage ordinal plaçait les retards rares inconnus d'un pli (6 à 8 mois) sous les meilleurs payeurs ; l'écart d'échelle signalé était faible (écart-type des rangs de 0,75 à 0,98) |
| 05/10/2026 | Traçabilité dans le fichier de résultats (commit, empreinte du train, niveau de nettoyage) | Audit : retrouver sur quel code et quelles données chaque résultat a été calculé |
| 05/10/2026 | Données : `creation_datasets_ML` part du niveau de nettoyage le plus élevé, trie par `ID` et contrôle ses colonnes contre le dataset de Streamlit | Ne dépendre que du nettoyage (reproductible après un clone) ; découpage identique à l'ancien |

## 12. Pistes, au-delà du projet

Une fois la méthode figée (reproductible, automatisée), elle peut s'appliquer à d'autres populations ou à d'autres points à améliorer, sans réécrire le code :
* **Deux modèles aiguillés par la règle métier** : la règle du contentieux répartit les clients du périmètre S12 entre la gestion saine et le contentieux à M ; un modèle par population.
  * **Modèle A, gestion saine** : le ML actuel.
  * **Modèle B, contentieux à M** : la question change. Environ 70 % de ces clients font défaut et la règle les prédit déjà tous en défaut ; le modèle B chercherait les clients qui ne feront **pas** défaut (ceux qui vont régulariser), pour réduire les fausses alertes de la règle. Son objectif et son étalon sont à définir à part. Ses variables propres : durée au contentieux (`NB_MOIS_CTX`), paiements pendant le retard… (la page 5.5 montre que le défaut augmente avec la durée au contentieux). Il disposerait de peu de clients (environ 2 400 dans le train du périmètre S12) : risque de surapprentissage plus fort, contenu par le seuil relatif et le plancher « bat le hasard ».
  * **L'expérience** : comparer **un seul modèle sur tout le périmètre S12** (contentieux compris) à **la règle suivie des deux modèles**, pour mesurer ce que la segmentation apporte. La comparaison avec la première itération et avec Yeh et Lien (2009), qui gardent le contentieux, devient aussi plus juste.
  * **Conditions** : pour chaque population, un jeu de données et un découpage propres, créés une seule fois, et un test lu une seule fois, distinct de celui du ML actuel.
* **v7 éventuelle, à tester seule après la v6 : une autre mise à l'échelle des `PAY_AMTn`.** Les paiements restent très étirés malgré les exclusions (médiane d'environ 2 000 NT$, maximum de 400 000 à 580 000 NT$) : après le `StandardScaler`, 96 % des clients sont tassés entre -1 et +1. Piste : un logarithme (`log(1 + montant)`) avant le `StandardScaler`, pour les seuls `PAY_AMTn` (les factures et le plafond sont dans des proportions raisonnables). Sans effet attendu sur les arbres ; gardée seulement si elle apporte un gain réel.
* **Moyenner plusieurs graines** (mise de côté le 05/10/2026, jugée trop lourde pour le moment) : après la boucle, calculer les probabilités hors pli des modèles aléatoires (RandomForest, CatBoost, MLP) avec plusieurs graines et en faire la moyenne, pour la référence comme pour le scénario comparé, et enregistrer un modèle moyenné. Elle réduirait le hasard interne des modèles (section 3) des deux côtés de la comparaison.
* **CatBoost en `Depthwise`** avec la taille des feuilles (section 5), s'il est encore dans le top 3 avec les variables finales.
