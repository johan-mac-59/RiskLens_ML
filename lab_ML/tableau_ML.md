# 📐 Matrice des Expérimentations & Traitements de Données

## 1. Niveaux de corrections cumulatifs

Les traitements sont structurés de manière strictement cumulative :
$$\text{Niveau 0} \subset \text{Niveau 1} \subset \text{Niveau 2} \subset \text{Niveau 3}$$

---

### 🟢 Niveau 0 (`corrections_niveau0`) — Nettoyage structurel de base
*Appliqué système à l'ensemble des datasets, y compris la baseline.*

* **`EDUCATION`** : Harmonisation sur l'échelle $[1, 4]$. Toute valeur $\notin \{1, 2, 3, 4\}$ est ramenée à `4` (*Autres*).
* **`MARRIAGE`** : Harmonisation sur l'échelle $[1, 3]$. Toute valeur $\notin \{1, 2, 3\}$ est ramenée à `3` (*Autres*).

---

### 🔵 Niveau 1 (`corrections_niveau1`) — Anomalies extrêmes & incohérences flagrantes
*Inclut l'intégralité du niveau 0.*

* **Outliers montants** : Exclusion des $4$ observations présentant $\text{PAY\_AMT}_n > 1\,000\,000$.
* **Comptes inactifs** : Suppression des $860$ comptes sans activité ($\text{PAY\_AMT}_n = 0$ et $\text{BILL\_AMT}_n \le 0$ sur l'ensemble des $6$ mois).
* **Anomalie isolée** : Correction manuelle du client `6783` ($\text{PAY} = 1$ sur $4$ mois alors que les paiements sont effectifs chaque mois $\implies$ rebinning à `0`).

---

### 🟠 Niveau 2 (`corrections_niveau2`) — Recalage de la codification `PAY_1 = 1` cohérence avec l'encours du mois
*Inclut l'intégralité des niveaux 0 et 1.*

* **Correction des incohérences `PAY_n = 1`** :
  * Si $\text{BILL\_AMT}_{n+1} \le 0 \implies \text{PAY}_n = \text{PAY}_{n+1}$ (parcours de `PAY_5` vers `PAY_1`, passes de vérification jusqu'à ce qu'aucune correction ne s'effectue).
  * Si $\text{BILL\_AMT}_{n+1} \le 0$ persistant $\implies \text{PAY}_n = 0$.

---

### 🔴 Niveau 3 (`corrections_niveau3`) — Recalage de la codification `PAY_1 = 1` par Ratio de Remboursement
*Inclut l'intégralité des niveaux précédents*
Analyse du ratio de remboursement en pourcentage $R = \frac{\text{PAY\_AMT1}}{\text{BILL\_AMT2}} \times 100$ pour corriger les faux retards en $M-1$ (`PAY_1 = 1`) :
* **Si $R \ge 90$ et $\text{PAY}_2 \le 0$** $\implies \text{PAY}_1 = \text{PAY}_2$ (facture soldée : payeur au comptant / à jour, reprise de la codification antérieure).
* **Tous les autres cas** (remboursement partiel ou nul) : $\text{PAY}_1 = 1$ maintenu, la vraie codification ne pouvant être déterminée.

> ⚠️ **Version actuelle (v2).** L'ancienne version (v1) utilisait des seuils à $R > 4$ % et $R > 10$ % et recopiait $\text{PAY}_2$ dans $\text{PAY}_1$ si $\text{PAY}_2 \ge 2$ : elle créait des `PAY_1 = 2` qui faisaient entrer des clients à tort dans la population contentieuse (CTX). Elle est abandonnée.
> **Les résultats ML du niveau 3 présentés ci-dessous ont été obtenus avec la v1.**

---

## 2. Scénarios d'Expérimentation Transversaux

Au sein de chaque niveau de correction, des scénarios autonomes sont appliqués de façon identique :

* **`S1` (Baseline)** : Aucun réencodage supplémentaire par rapport au niveau de correction actif.
* **`S2` (Plafonnement des impayés)** : Clamping des retards sévères ($\text{PAY}_n > 2 \implies 2$).
* **`S3` (Filtrage encours actif)** : Restriction de la population aux clients avec $\text{BILL\_AMT1} > 0$.
* **`S4` (Simplification clients à Jour)** : Regroupement des statuts sans retard ($\text{PAY}_n \in \{-2, -1\} \implies 0$).
* **`S5` (Simplification plafonnement des impayés et clients à jours)** : S2 + S4
* **`S6` (Simplification plafonnement des impayés, des clients à jours et filtrage des encours actifs uniquement)** : S2 + S3 + S4
* **`S7` (Plafonnement léger des impayés)** : Clamping des retards sévères ($\text{PAY}_n >3 \implies 3$).
* **`S8` (Filtrage encours actif + plafonnement léger des impayés)** : S3 + S7
* **`S9` (Filtrage encours actif + Simplification clients à Jour)** : S3 + S4
* **`S10` (Simplification plafonnement des impayés + Filtrage encours actif)** : S2 + S3
* **`S11` (Suppression des clients atypiques gros plafond)** : Restriction de la population aux clients avec $\text{LIMIT\_BAL} \leq 500000$
* **`S12` (Filtrage encours actif + suppression des clients atypiques gros plafond)** : S3 + S11
* **`S13` (Suppression de la colonne PAY_1)** : On retire une colonne très pollulée avec df = df.drop(columns=['PAY_1'])
* **`S14` (Suppression des colonnes antérieures à PAY_1)** : on retire les colonnes antérieures à 'PAY_1' pour vérifier son poids seul avec et sans correction avec df = df.drop(columns=['PAY_2','PAY_3','PAY_4','PAY_5','PAY_6'])
* **`S15` (Remplacement de 'PAY_1' par un ratio de paiement sur dette)** : $\text{RATIO\_PAY\_1} = \begin{cases} \min\left(\max\left(\frac{\text{PAY\_AMT1}}{\text{BILL\_AMT2}}, \, 0.0\right), \, 2.0\right) & \text{si } \text{BILL\_AMT2} > 0 \\ 1.0 & \text{si } \text{BILL\_AMT2} \le 0 \end{cases}$




### Méthodologie

Afin d'évaluer les performances de telle ou telle modification du jeu de données ou d'une variable et d'avoir un score unique souverain dans mes décisions, j'utilise 2 métriques d'optimisation :
- ROC AUC indirectement utilisé par I-Cheng Yeh et Che-hui Lien pour évaluer les performances de leurs modèles
- F2 score très adapté au milieu bancaire qui pénalise assez fortement la non détection de cas positifs
J'applique la moyenne de ces 2 métriques pour chaque modèle pour obtenir un score moyen que j'uniformise à toutes mes expérimentations
**Le seul critère de choix d'un scénario ou d'un modèle est ce score de décision, mesuré en validation croisée sur le train.** Les résultats sur le jeu de test sont donnés à titre d'information (contrôle de la généralisation), jamais comme critère de choix.

### Résultats de ces expérimentations sur le dataset initial

S1 sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score de décision : 0.6881 | Recall  0.6310
🥈 RandomForest — Score de décision : 0.6876
🥉 LogisticRegression — Score de décision : 0.6492

**Résultats de `S2` :**  
🥇 RandomForest — Score de décision : 0.688 | Recall  0.6350
🥈 CatBoost — Score de décision : 0.6874
🥉 LogisticRegression — Score de décision : 0.6494
=> neutre, à essayer en combinaison avec un autre scenario pour vérifier son impact

**Résultats de `S3` :**  
🥇 CatBoost — Score de décision : 0.6934 | Recall  0.6218
🥈 RandomForest — Score de décision : 0.6915
🥉 LogisticRegression — Score de décision : 0.6613
Hausse généralisée des performances de tous les modèles et généralisation des bonnes performances à tous les modèles, plus aucun n'est à la traîne mais légère baisse du recall  
=> scénario conservé  

**Résultats de `S10` :** 
🥇 CatBoost — Score de décision : 0.6924 | 0.6231
🥈 RandomForest — Score de décision : 0.6918
🥉 LogisticRegression — Score de décision : 0.6607
Pas d'amélioration par rapport à `S3`
=> scénario écarté  

**Résultats de `S7` :**  
🥇 CatBoost — Score de décision : 0.6882 | Recall  0.6306
🥈 RandomForest — Score de décision : 0.6876
🥉 LogisticRegression — Score de décision : 0.6487
=> scénario mis de côté

**Résultats de `S8` :**  
🥇 RandomForest — Score de décision : 0.6924 | Recall  0.6233
🥈 CatBoost — Score de décision : 0.692
🥉 LogisticRegression — Score de décision : 0.6607
Aucune amélioration par rapport à `S3`  
=> scénario écarté

**Résultats de `S4` :**  
🥇 CatBoost — Score de décision : 0.6872 | Recall  0.6299
🥈 RandomForest — Score de décision : 0.6864
🥉 LogisticRegression — Score de décision : 0.6581
légère baisse des performances
=> scénario écarté

**Résultats de `S9` :**  
🥇 RandomForest — Score de décision : 0.6915 | Recall  0.621
🥈 CatBoost — Score de décision : 0.6911
🥉 LogisticRegression — Score de décision : 0.6669
Pas d'amélioration par rapport à `S3`
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score de décision : 0.6924 | Recall  0.6369
🥈 RandomForest — Score de décision : 0.6899
🥉 LogisticRegression — Score de décision : 0.6485
Très légère amélioration visible  
perte de performance constaté sur le jeu de tests inhabituel mais pas anormal
=> scénario conservé 

**Résultats de `S12` :**  
🥇 CatBoost — Score de décision : 0.6889 | Recall  0.6136
🥈 RandomForest — Score de décision : 0.687
🥉 LogisticRegression — Score de décision : 0.6559
Phénomène rare : meilleurs résultats sur le test que sur la validation  
Performances moins bonnes que S3 seul ou S11 seul
=> scénario écarté

**Résultats de `S13` :**  
🥇 CatBoost — Score de décision : 0.6572 | Recall  0.6058
🥈 RandomForest — Score de décision : 0.6543
🥉 LogisticRegression — Score de décision : 0.6164
Performances dégradées de 0.0309 et recall abaissé de 0.0252
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score de décision : 0.683 | Recall  0.6238
🥈 RandomForest — Score de décision : 0.6815
🥉 LogisticRegression — Score de décision : 0.646
Performances dégradées
=> scénario écarté

**Résultats de `S15` :**  
🥇 CatBoost — Score de décision : 0.6576 | Recall  0.6073
🥈 RandomForest — Score de décision : 0.6528
🥉 LogisticRegression — Score de décision : 0.6199
Performances dégradées de plus de 3 points sur le score
=> scénario écarté

**Conclusion**  
Pas de surapprentissage pour les scnéarii validés.  
Seul les scénari `S3` et `S11` apportent une réelle valeur ajoutée et répondent de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

### Résultats de ces expérimentations sur le dataset avec niveau 1 de corrections

*Passage à cv=3 dans GridSearchCV pour gagner du temps sur les 2 premiers entrainements rapides.*
`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score de décision : 0.6818 | Recall  0.6087
🥈 RandomForest — Score de décision : 0.6807
🥉 LogisticRegression — Score de décision : 0.652
Légère baisse des performances par rapport au niveau de correction 0, notamment 2 points de recall

**Résultats de `S2` :**  
🥇 CatBoost — Score de décision : 0.6817 | Recall  0.6081
🥈 RandomForest — Score de décision : 0.6805
🥉 LogisticRegression — Score de décision : 0.6534
Performances stables
=> à combiner éventuellement avec d'autres scénarii

**Résultats de `S3` :**  
🥇 RandomForest — Score de décision : 0.692 | Recall  0.6191
🥈 CatBoost — Score de décision : 0.6915
🥉 LogisticRegression — Score de décision : 0.6621
Améliorations de toutes les métriques
=> scénario conservé

**Résultats de `S10` :**  
🥇 RandomForest — Score de décision : 0.6913 | Recall  0.6174
🥈 CatBoost — Score de décision : 0.6897
🥉 LogisticRegression — Score de décision : 0.6602
Très légère régression par rapport à `S3` seul
=> scénario écarté

**Résultats de `S7` :**  
🥇 CatBoost — Score de décision : 0.681 | Recall  0.6109
🥈 RandomForest — Score de décision : 0.6805
🥉 LogisticRegression — Score de décision : 0.653
Performances équivalentes à `S1`
=> à combiner avec un autre scénario

**Résultats de `S8` :** 
🥇 RandomForest — Score de décision : 0.6908 | Recall  0.6191
🥈 CatBoost — Score de décision : 0.6906
🥉 LogisticRegression — Score de décision : 0.6601
Pas d'améliorations par rapport à `S3` seul
=> scénario écarté

**Résultats de `S4` :**  
🥇 RandomForest — Score de décision : 0.6789 | Recall  0.6040
🥈 CatBoost — Score de décision : 0.6774
🥉 LogisticRegression — Score de décision : 0.6573
Légère baisse des performances
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score de décision : 0.6867 | Recall  0.6148
🥈 RandomForest — Score de décision : 0.6841
🥉 LogisticRegression — Score de décision : 0.6537
baisse des performances légères
Phénomène notable : perte de recall sur le jeu de tests
=> scénario écarté

**Résultats de `S13` :**  
🥇 CatBoost — Score de décision : 0.6467 | Recall  0.5806
🥈 RandomForest — Score de décision : 0.6455
🥉 LogisticRegression — Score de décision : 0.6296
Performances dégradées de 0.0351 et recall abaissé de 0.0281
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score de décision : 0.6776 | Recall  0.6075
🥈 RandomForest — Score de décision : 0.6761
🥉 LogisticRegression — Score de décision : 0.6467
LR a un recall de 0.6516 !
performances légèrement moins bonnes
=> scénario écarté

**Résultats de `S15` :**  
🥇 CatBoost — Score de décision : 0.6472 | Recall  0.5771
🥈 RandomForest — Score de décision : 0.6373
🥉 LogisticRegression — Score de décision : 0.6298
Perte de plus de 3 points de performances et recall
=> scénario écarté

**Conclusion**  
Surapprentissage léger sur certains modèles.  
Seul le `scénario 3` apporte une réelle valeur ajoutée et répond de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

### Résultats de ces expérimentations sur le dataset avec niveau 2 de corrections

`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score de décision : 0.6807 | Recall  0.6097
🥈 RandomForest — Score de décision : 0.679
🥉 LogisticRegression — Score de décision : 0.649
Légère baisse des performances par rapport au dataset initial
Très légère baisse des performances et recall stable par rapport aux corrections de niveau 1

**Résultats de `S2` :**  
🥇 CatBoost — Score de décision : 0.6802 | Recall  0.6095
🥈 RandomForest — Score de décision : 0.679
🥉 LogisticRegression — Score de décision : 0.6485
Perfomances stables
=> scénario écarté

**Résultats de `S3` :**  
🥇 RandomForest — Score de décision : 0.6917 | Recall  0.6181
🥈 CatBoost — Score de décision : 0.6909 | 0.6195
🥉 LogisticRegression — Score de décision : 0.6595
Améliorations notables de toutes les performances
=> scénario conservé

**Résultats de `S10` :**  
🥇 CatBoost — Score de décision : 0.6913 | Recall  0.6210
🥈 RandomForest — Score de décision : 0.6906 | 0.6185
🥉 LogisticRegression — Score de décision : 0.6596
pas d'améliorataion par rapport à `S3` seul
=> scénario écarté

**Résultats de `S7` :**  
🥇 CatBoost — Score de décision : 0.6808 | Recall  0.6091
🥈 RandomForest — Score de décision : 0.679
🥉 LogisticRegression — Score de décision : 0.6484
Performances équivalentes à `S1`
=> scénario écarté

**Résultats de `S8` :** 
🥇 RandomForest — Score de décision : 0.6918 | Recall  0.6183
🥈 CatBoost — Score de décision : 0.6905
🥉 LogisticRegression — Score de décision : 0.6597
Pas d'amélioration par rapport à `S3` seul  
=> scénario écarté

**Résultats de `S4` :**  
🥇 CatBoost — Score de décision : 0.6787 | Recall  0.6063
🥈 RandomForest — Score de décision : 0.6779
🥉 LogisticRegression — Score de décision : 0.6533
Perte de performances
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score de décision : 0.687 | Recall  0.6158
🥈 RandomForest — Score de décision : 0.683
🥉 LogisticRegression — Score de décision : 0.65
Très légère amélioration des performances 
=> scénario conservé

**Résultats de `S12` :**  
🥇 CatBoost — Score de décision : 0.6875 | Recall  0.6169
🥈 RandomForest — Score de décision : 0.6842
🥉 LogisticRegression — Score de décision : 0.6528 
Performances similaires à `S11` mais inférieures à `S3`  
=> scénario écarté

**Résultats de `S13` :**  
🥇 CatBoost — Score de décision : 0.6467 | Recall  0.5806
🥈 RandomForest — Score de décision : 0.6451
🥉 LogisticRegression — Score de décision : 0.6295
Performances dégradées de 0.0340 et recall abaissé de 0.0291
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score de décision : 0.677 | Recall  0.6055
🥈 RandomForest — Score de décision : 0.675
🥉 LogisticRegression — Score de décision : 0.6409

**Résultats de `S15` :**  
🥇 CatBoost — Score de décision : 0.6472 | Recall  0.5814
🥈 RandomForest — Score de décision : 0.6402
🥉 LogisticRegression — Score de décision : 0.6295
Perte de plus de 3 points de performances et pres de 3 points de recall
=> scénario écarté

**Conclusion**  
Pas de surapparentissage.  
Seuls les `S3` et `S11` apportent une réelle valeur ajoutée et répondent de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.
Performances légèrement moins bonnes
=> scénario écarté

### Résultats de ces expérimentations sur le dataset avec niveau 3 de corrections
*Résultats obtenus avec la v1 du niveau 3 (abandonnée, voir section 1).*

`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score de décision : 0.6808 | Recall  0.611
🥈 RandomForest — Score de décision : 0.6786
🥉 LogisticRegression — Score de décision : 0.6431
Un tout petit peu moins bon que le niveau de correction 0, équivalent aux niveau 1 et 2

**Résultats de `S2` :**  
🥇 CatBoost — Score de décision : 0.6789 | Recall  0.6093
🥈 RandomForest — Score de décision : 0.678
🥉 LogisticRegression — Score de décision : 0.6423
pas d'amélioration des performances  
=> scénario écarté

**Résultats de `S3` :**  
🥇 CatBoost — Score de décision : 0.6907 | Recall  0.6214
🥈 RandomForest — Score de décision : 0.6891
🥉 LogisticRegression — Score de décision : 0.66
Amélioration générales de toute les performances
=> scénario conservé

**Résultats de `S7` :**  
🥇 CatBoost — Score de décision : 0.6805 | Recall  0.6107
🥈 RandomForest — Score de décision : 0.6786
🥉 LogisticRegression — Score de décision : 0.6432
Pas d'amélioration par rapport à S1  
=> scénario écarté

**Résultats de `S8` :**  
🥇 CatBoost — Score de décision : 0.6908 | Recall  0.6212
🥈 RandomForest — Score de décision : 0.6891
🥉 LogisticRegression — Score de décision : 0.6599
Performances stables par rapport à `S3` seul
=> scénario à mettre de côté

**Résultats de `S4` :**  
🥇 CatBoost — Score de décision : 0.6793 | Recall  0.6093
🥈 RandomForest — Score de décision : 0.6763
🥉 LogisticRegression — Score de décision : 0.6516
pas d'amélioration des performances
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score de décision : 0.6856 | Recall  0.6170
🥈 RandomForest — Score de décision : 0.6824
🥉 LogisticRegression — Score de décision : 0.6467
Amélioration des performances
Phénomène notable : baisse du recall de 2 points du recall sur le test
=> scénario conservé

**Résultats de `S12` :**  
🥇 CatBoost — Score de décision : 0.686 | Recall  0.6209
🥈 RandomForest — Score de décision : 0.6842
🥉 LogisticRegression — Score de décision : 0.6519
Phénomène notable : résultats meilleurs sur le jeu de tests
Très légère amélioration des performances par rapport à `S11`
Pas d'amélioration par rapport à `S3`
=> scénario conservé en lieu et place de `S11`

**Résultats de `S13` :**  
🥇 CatBoost — Score de décision : 0.6467 | Recall 0.5806
🥈 RandomForest — Score de décision : 0.6417
🥉 LogisticRegression — Score de décision : 0.6295 | Recall 0.6441
Performances dégradées de 0.0341 et recall abaissé de 0.0304
A noter un recall élevé pour LR
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score de décision : 0.6768 | Recall  0.6099
🥈 RandomForest — Score de décision : 0.6736
🥉 LogisticRegression — Score de décision : 0.6337
Performances légèrement dégradées
=> scénario écarté

**Résultats de `S15` :**  
🥇 CatBoost — Score de décision : 0.6472 | Recall  0.5814
🥈 RandomForest — Score de décision : 0.6405
🥉 LogisticRegression — Score de décision : 0.6281
Dégradation de plus de 3 points du score et du recall
=> scénario écarté

**Conclusion**  
Pas de surapparentissage.  
Seuls les `S3` et `S12` apportent une réelle valeur ajoutée et répondent de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.


### Conclusion sur les différents niveaux de nettoyage et leurs scénarii

A modèle fixe, les performances DE `S3` sur les différents niveaux de nettoyages est quasi stable. Il semble préférable de travailler sur le jeu de données avec un nettoyage de niveau 3 et un scénario 3. Les variables implémentées par la suite dépendant de la propreté des données n'en seront que meilleures et fiables.  
Le scénario `13` visait à comparer la perte de performances selon le niveau de correction si on retirait la colonne 'PAY_1'. Statistiquement, j'aurais tendance à dire que le niveau 0 de correction a été le moins impacté par une perte de performances brute. J'en concluerais que la correction apportée sur PAY_1 est positive en terme d'impact sur la prédiction des modèles.  
Les scénarii `14` et `15` visaient à déterminer l'importance de la colonne PAY_1 en l'état. Corrigée ou non, elle apporte une information primordiale pour la prédiction du défaut.  

Si je décide de conserver le niveau de correction 3 pour la suite de mon feature engineering, il est préférable de partir sur le scénario `12` (qui inclut `S3`) qui a les memes performances que ce dernier mais restreint très légèrement la population à la masse principale de notre dataset et qui correspond à la clientèle standard

**Je choisis de travailler sur de nouvelles variables à partir du jeu de données corrigé de niveau 3, uniquement sur les clients avec un encours positif à M-1 et avec un plafond de crédit inférieur ou égal à 500 000 NT$.**


---

## 3. Features

**Méthodologie**  
Seuls les 3 modèles les plus performants ci dessus restent employés pour évaluer les performances des nouvelles variables utilisées.  
Les apprentissages sont simplifiés piur gagner en rapidité et limiter au maximul le surapprentissage.  

Le jeu de données utilisé est celui de niveau de corrections 3 (v1, abandonnée depuis : voir section 1).  
Ne sont traités que les clients avec un encours positif strict en M-1, et un plafond de crédit au maximum de 500 000 NT$. 

Je crée un pipeline simplifié
`S12_0` référence
🥇 CatBoost — Score de décision : 0.6865 | Recall  0.6196
🥈 RandomForest — Score de décision : 0.6771
🥉 LogisticRegression — Score de décision : 0.6515

`S12_1` : ajout des colonnes ratio_BILL_LIMITn = BILL_AMTn / LIMIT_BAL
Limite à 200% pour limiter le bruit de certaines valeurs aberrantes
Limite basse à 0% pour les encours non utilisés ou négatifs
🥇 CatBoost — Score de décision : 0.6877 | Recall  0.6211
🥈 RandomForest — Score de décision : 0.6791
🥉 LogisticRegression — Score de décision : 0.6507
=> nouveau scénario privilégié

`S12_2` : `S12_1` + 'AGE' décomposé en bins pertinents
L'âge n'est presque pas utilisé par les modèles pour prédire le défaut. Et pour cause, j'ai constaté que l'âge n'avait de sens que s'il est traité par tranches pour le mettre en corrélation avec le défaut de paiement.
Nouvelle Feature : tranches d'âge 'AGE_BUCKET' en remplacement de 'AGE'.  
🥇 CatBoost — Score de décision : 0.6866 | Recall  0.6175
🥈 RandomForest — Score de décision : 0.6773
🥉 LogisticRegression — Score de décision : 0.6505
=> scénario écarté

`S12_3` : `S12_1` + ajout des colonnes de ratio de paiement / encours utilisé
Elles indiquent au modèle indirectement si le client paie sa dette ou non, et quelle proportion, en évitant les NaN (si un client n'a pas de dette à M-1, on considère qu'il a payé 100%)
$\text{ratio\_PAY\_BILLn} = \begin{cases} \min\left(\max\left(\frac{\text{PAY\_AMTn}}{\text{BILL\_AMTn+1}}, \, 0.0\right), \, 2.0\right) & \text{si } \text{BILL\_AMTn+1} > 0 \\ 1.0 & \text{si } \text{BILL\_AMTn+1} \le 0 \end{cases}$
🥇 CatBoost — Score de décision : 0.6878 | Recall  0.6180
🥈 RandomForest — Score de décision : 0.6787
🥉 LogisticRegression — Score de décision : 0.6593
*Même définition que la colonne `ratio_PAY_BILLn` créée dans `02_01_nettoyage` (écrêtée entre 0 et 200 %, 100 % sans facture exigible), exprimée ici en fraction (0 à 2, 1 = 100 %).*  
pas de gain, les informations étaient déjà présentes
=> scnéario écarté

`S12_4` : `S12_0` + substitution des colonnes PAY_AMTn et BILL_AMTn au profit des ratios de `S12_1` ration_BILL_LIMITn et `S12_3` ratio_PAY_BILLn
🥇 CatBoost — Score de décision : 0.686 | Recall  0.6150
🥈 RandomForest — Score de décision : 0.6773
🥉 LogisticRegression — Score de décision : 0.6505
pas de gain
=> scénario écarté

`S12_5` : `S12_1` + classer les clients par leur type d'usage (paiement différé total, crédit, autres)
pour ce faire, on va utiliser les colonnes ratio_PAY_BILLn (PAY_AMTn / BILL_AMT(n+1)) pour regarder la médiane par client ratio_PAY_to_BILL_median et laisser les modèles faire leur propre découpage pour le lier au défaut de paiement
🥇 CatBoost — Score de décision : 0.6878 | Recall  0.6226
🥈 RandomForest — Score de décision : 0.6793
🥉 LogisticRegression — Score de décision : 0.6569
Très légère amélioration des performances par rapport à `S12_1`
=> nouveau scnéario privilégié

`S12_6` : `S12_5` + ajout d'un indicateur d'ancienneté d'activité du compte  
justement pour aider les modèles à mieux comprendre quoi faire du ratio de paiement médian et notamment les '-1'
Indicateur d'activation récente du crédit (entre M-1 et M-4 sans encours sur tous les mois précédent)  
on va regarder l'activation des comptes sur la période et les taguer comme suit :
- compte toujours actif : 7
- actif depuis m-4 : 4
- actif depuis m-3 : 3
- actif depuis m-2 : 2
- actif depuis m-1 : 1
intéret : Ajouter un flag pour les clients récents qui peuvent avoir un 'ratio_PAY_to_BILL_median' trompeur  
De plus, cela ajoute un indicateur aux modèles : client récent, activation de compte, réactivation de compte, sortie de contentieux.  
🥇 CatBoost — Score de décision : 0.6885 | Recall  0.6247
🥈 RandomForest — Score de décision : 0.6789
🥉 LogisticRegression — Score de décision : 0.6622
Cette variable a un impact légèrement positif sur les prédictions
=> nouveau scénario privilégié

`S12_7` : `S12_6` + Codification contentieux
J'ai détecté dans mon EDA un phénomène avec PAY_n = 2, il ne s'agit pas toujours d'un retard de 2 mois constaté
Créer une variable "flag" appelée 'CTX' qui est True si :
- PAY_n == 2 sur les 6 mois
- PAY_n == 2 et ((PAY_(n+1)>2) & (BILL_AMT(n+1)>0) & (PAY_AMTn == 0)) *(convention corrigée le 27/09/2026 : la facture exigible au mois n est BILL_AMT(n+1) ; les résultats ci-dessous ont été obtenus avec BILL_AMTn)*
sinon False
🥇 CatBoost — Score de décision : 0.6875 | Recall  0.6198
🥈 RandomForest — Score de décision : 0.6772
🥉 LogisticRegression — Score de décision : 0.66
Ce premier résultat (moins bon que `S12_6` et surtout moins bon qu'attendu malgré une variable ultra discriminante implémentée) sans besoin de brider les modèles qui sont d'habitude en surapprentissage est un message, d'autant plus que les arbres n'utilisent pas cette variable : il y a peut etre un sous apprentissage par manque de profondeur. Je décide d'augmenter les fenêtres de paramètres pour ce scénario :  
🥇 CatBoost — Score de décision : 0.6875 | Recall  0.6198
🥈 RandomForest — Score de décision : 0.6846
🥉 LogisticRegression — Score de décision : 0.66
Aucune évolution donc pas la cause du problème. Probable que les modèles avaient déjà compris par eux-mêmes cette anomalie
Autre test pour vérifer un aspect étonnant (progression de 2 points de toutes les perf pour tous les modèles sur le jeu de test) : répartir équitablement les clients présumés 'CTX' :
🥇 CatBoost — Score de décision : 0.6872 | Recall  0.6221
🥈 RandomForest — Score de décision : 0.6848
🥉 LogisticRegression — Score de décision : 0.6562
Même si les résultats ne progressent pas (CTX n'est pas uniformisé dans les boucles du cross_validation), les résultats sur le jeu de tests surperforment encore davantage que précédemment, atteignant des scores jamais atteints auparavant. C'est la preuve que la variable 'CTX' a un impact fort. Ici, je suis confronté à un dilemne : conserver cette variable et l'intégrer de manière uniforme partout et sortir cette clientèle du circuit des clients sains, en entreprise j'aurais pu avoir ma réponse sur cette classification, mais je ne peux que supposer ici.
**71.27% des clients ayant un encours et étant taggé contentieux sont en défaut de paiement à M.**  
**Dans le jeu de données initial, 77.55% de taux de défaut de paiement pour les clients avec PAY_n = 2 sur les 6 mois**
Ces clients représentent 3.61% du jeu de données nettoyé. J'ai affaire à une anomalie dans les codifications de risques et de comportement des paiements et encours, couplé à un taux de défaut énorme





`Remonter cv dans GridSearchCV quand on approfondit les modèles`

---

## 4. Redémarrage du ML : dataset nettoyé de sa population contentieuse

**Pourquoi redémarrer**  
La variable `CTX` de `S12_7` a mis en évidence une poche de clients au taux de défaut très élevé qui plafonnait les modèles. Elle est désormais isolée par une **règle métier** (`src/05_02_EDA_contentieux.ipynb`, définition 2) : les clients au CTX sont retirés du dataset ML et prédits en défaut par la règle. Le ML repart sur la population restante, avec des indicateurs d'historique à la place des anciens codes bruts.  
Les résultats des sections 2 et 3 ne sont plus directement comparables : ils portaient sur la population complète du périmètre `S12`.

**Référence de départ : la règle seule, évaluée sur la population qu'elle traite** (clients au CTX, tous prédits en défaut)  
*Chiffres de la définition 2 révisée le 27/09/2026 (`05_02_EDA_contentieux`, section 9.1).*

| Jeu | Clients CTX | Vrais positifs | Faux positifs | Précision | Recall | F2 | Part des défauts du dataset captés |
|---|---|---|---|---|---|---|---|
| Train (S12) | 2 403 | 1 690 | 713 | 70.33 % | 100 % | 0.9222 | 35.38 % |
| Test (S12) | 601 | 427 | 174 | 71.05 % | 100 % | 0.9246 | 35.73 % |
| Dataset initial (30 000) | 3 013 | 2 124 | 889 | 70.49 % | 100 % | 0.9228 | 32.01 % |

Sur ce périmètre, le recall vaut 100 % par construction et le ROC AUC n'est pas défini (une seule classe prédite) : la précision est la métrique qui compte. Les défauts non captés par la règle relèvent du ML.

**Comment évaluer le nouveau ML**
* Le modèle est entraîné et validé sur la population hors CTX (même split que le notebook contentieux).
* Le **système complet** est évalué sur le test : prédiction de la règle pour les clients au CTX, prédiction du modèle pour les autres. C'est ce score qui se compare à la règle seule, à `S12_6` / `S12_7` et à l'étude de Yeh.
* Pour le ROC AUC du système complet, les clients au CTX reçoivent une probabilité fixe (par exemple leur taux de défaut observé sur le train) afin de les intégrer à la courbe ROC.

### Features et pistes à tester (issues de `src/05_02_EDA_contentieux.ipynb`)
*Liste de travail : rien n'est encore testé. Fonctions de calcul : `corriger_faux_codage` (section 3), `recodage_pay1` (section 6.1) et `statut_ctx_regle2` (section 6 du notebook contentieux), version révisée du 27/09/2026, recodage du mois de transition révisé le 30/09/2026.*

**Définition du CTX retenue : définition 2 (deux codes >= 2 successifs)**
* Dans l'historique, un passage au CTX nécessite deux codifications >= 2 successives ; un 2 isolé est un **retard régularisé**. Un 2 isolé en M-6 est considéré comme un passage au CTX par défaut (M-7 non observé).
* À M-1, tout code >= 2 place le client au CTX, sauf facture payée à 90 % ou plus en M-1 ou en M-2 (**retard payé**, traité comme une régularisation présumée au plus tard en M) : retard isolé (PAY_2 < 2) → `FLAG_RETARD` = 1, `MOIS_SORTIE_RETARD` = 0 ; retard qui termine une série (PAY_2 >= 2) → `FLAG_CTX` = 1, `MOIS_SORTIE_CTX` = 0.
* Correction des faux 2 : faux codage neutralisé ; compte endormi : codes >= 2 posés sur une facture nulle neutralisés pour le CTX, flag `SURVEILLANCE_RECENTE` conservé (révision du 27/09/2026). Recodage du mois de transition (révisé le 30/09/2026) : remis à 2 si deux factures exigibles sont impayées ; facture de M-1 soldée (>= 90 %) : retour au code d'avant le retard ; sinon inchangé (ancien recodage en -1 dès 10 % supprimé).
* La population CTX est très proche de celle de la règle 1 (les différences viennent des comptes endormis) ; la définition 2 **affine le grain des retards** transmis au ML.
* Dans les règles du CTX, un ratio de paiement sans facture exigible vaut 0 (pas de preuve de paiement) ; la feature `ratio_PAY_BILLn` (100 % sans facture) ne sert pas à définir le CTX.

**Changement de périmètre**
* Les clients `CTX` à M (`FLAG_CTX` = 1 et `MOIS_SORTIE_CTX` = -1) sont **retirés du dataset ML** et prédits en défaut par une règle métier. Le ML traite les clients `Retard considéré régularisé M-1`, `Sorti`, `Retard régularisé` et `Jamais CTX`.
* Split commun avec le notebook contentieux : périmètre `S12`, 80/20, `stratify=dpnm`, `random_state=42`.
* Évaluation du **système complet** (règle CTX + modèle) sur le même test, pour rester comparable à `S12_6` / `S12_7`, à la règle `PAY_n >= 2` et à l'AUC de Yeh (0.77).
* La variable `CTX` de `S12_7` est remplacée par les features ci-dessous.

**Features candidates** (dans l'ordre logique de calcul : chaque étape travaille sur les codes produits par la précédente ; les comptages de codes >= 2 se font en dernier, sur les codes définitifs)

*Étape 1 : correction des faux 2 (`corriger_faux_codage`)*
* `SURVEILLANCE_RECENTE` : 1 si le client a reçu un faux 2 sur compte endormi (code 2 posé sur une facture nulle, sans paiement ni encours avant) ; ces codes ne comptent pas pour le CTX.
* `FAUX_CODAGE` : 1 si un faux 2 a été neutralisé (client qui venait de payer ou avait un encours).

*Étape 2 : recodage du mois de transition (`recodage_pay1`, sur les codes corrigés)*
* `PAY_1_recode` : PAY_1 recodé au mois de transition (PAY_2 >= 2 et PAY_1 <= 1) selon les paiements, en remplacement de `PAY_1`.

*Étape 3 : statuts (`statut_ctx_regle2`, codes corrigés et `PAY_1_recode` en M-1)*
* `FLAG_CTX` : marqueur intemporel, 1 si le client a eu deux codes >= 2 consécutifs sur les 6 mois (codes posés sur une facture nulle exclus) ; un 2 isolé en M-6 ou en M-1 compte par défaut (suite ou antécédent inconnu), sauf retard payé isolé à M-1. 0 sinon.
* `MOIS_SORTIE_CTX` : mois de la dernière sortie du CTX (1 à 5), 0 = sortie présumée en M (retard payé qui termine une série), -1 s'il n'y a pas de sortie (client encore au CTX ou jamais au CTX). Variante à tester si le mélange perturbe la régression logistique : une valeur dédiée pour « aucun passage », distincte du 0.
* `FLAG_RETARD` : 1 si le client a eu un retard isolé (un seul mois à >= 2) régularisé sur la période, ou un retard payé isolé à M-1.
* `MOIS_SORTIE_RETARD` : 0 = retard payé isolé à M-1 (code >= 2 à M-1, PAY_2 < 2, mais facture payée à 90 % ou plus en M-1 ou M-2, régularisation présumée), 1 à 4 = mois du retour sous 2 après le dernier retard isolé, -1 = aucune régularisation. La valeur -1 mélange jamais CTX et sortis : à lire avec `FLAG_RETARD` et `FLAG_CTX`, et à traiter en catégoriel pour la régression logistique.

*Étape 4 : comptages, en dernier, sur les codes définitifs (ceux utilisés par `statut_ctx_regle2` : faux codages et comptes endormis neutralisés, `PAY_1_recode` en M-1) ; colonnes pas encore créées*
* `NB_MOIS_CTX` : durée du dernier passage au CTX au sens de `FLAG_CTX`, en mois consécutifs à >= 2 (non cumulée : un client avec deux passages séparés n'est compté que sur le dernier) ; 0 si `FLAG_CTX` = 0 (retard isolé ou retard payé isolé exclus). À mois de sortie égal, un passage plus long reste le plus souvent associé à un risque plus élevé (étude sur le train avec la définition retenue : `src/05_04_EDA_codification1.ipynb`, section 5.1).
* `CUMUL_INCIDENT` : nombre total de mois avec un code >= 2 sur les 6 mois, consécutifs ou non. Complète `NB_MOIS_CTX` : mesure la fréquence des incidents sur la période, quand `NB_MOIS_CTX` mesure la durée du dernier passage.

*Hors codes de retard (montants seuls, indépendant de l'ordre ci-dessus)*
* Nombre de mois sans paiement sur la période (utilisé pour décrire les statuts, jamais testé comme feature).

**Scénarios à comparer**
* Niveau de correction : `cleaned2` vs `cleaned3` (niveau 3 v2).
* Deux usages métier :
  * **Comportemental** : codes PAY_n conservés (complets, ou version réduite PAY_1 + agrégats).
  * **Sans codes risque** : PAY_n supprimés, on garde montants, ratios, démographie et flags CTX. Mesurer le coût en performance.
* Traitement des clients entrés au CTX en M-1 avec un seul 2 : au CTX (choix actuel) ou dans le ML avec un flag de retard en cours (définition 2 appliquée jusqu'à M-1).

**Points tranchés / ouverts**
* **Tranché** : règle de transition, PAY_1 n'est remis à 2 que si deux factures exigibles consécutives (`BILL_AMT3` et `BILL_AMT2` > 0) sont impayées (section 3.3 du notebook contentieux).
* **Tranché** : définition 2 retenue, avec 2 isolé en M-6 considéré comme passage au CTX et retard payé à M-1.
* **Tranché (27/09/2026)** : retard payé qui termine une série → `FLAG_CTX` = 1 et `MOIS_SORTIE_CTX` = 0 ; faux 2 sur compte endormi → seul `SURVEILLANCE_RECENTE` (se cumule avec `FLAG_CTX` si d'autres codes >= 2 surviennent sur une vraie dette) ; ratio sans facture exigible = 0 dans les règles du CTX.
* Code 2 posé le mois où la facture est payée en totalité (historique) : anomalie documentée, non corrigée.


## Problèmes rencontrés

### Redémarrage suite à un début d'encodage sur certaines colonnes  
J'ai testé :
1. sans encodage (les variables catégorielles étaient des nombres entiers)
2. lors de l'ajout de tranches d'âge, l'encodage est devenu obligatoire, je ne pouvais plus laisser des variables sans encodage, cela perturbait certaines de mes modèles testés, j'ai testé un OrdinalEncoder pour les tranches d'âge puis sur les PAY_n
3. j'ai testé un OneHotEncodeur sur les catégories non ordonnées et un OrdinalEncoder sur les catégories ordonnées
Après visualisation des résultats, le meilleur paramétrage était un encodage mixte : la solution `3`.  
J'ai également détecté que mon comparatif et ma matrice de confusion se faisait sur les résultats d'entrainement -> j'ai modifié pour que ce soit les performances de validation qui soient exposées et comparées au test => Forte diminution de la perte de recall
=> je vais relancer les 6 scnearii précédents pour tester vérifier si les résultats précédents se vérifiaient toujours