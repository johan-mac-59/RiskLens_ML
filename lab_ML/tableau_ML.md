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
* **Comptes inactifs** : Traitement des $860$ comptes sans activité ($\text{PAY\_AMT}_n = 0$ et $\text{BILL\_AMT}_n \le 0$ sur l'ensemble des $6$ mois).
* **Anomalie isolée** : Correction manuelle du client `6783` ($\text{PAY} = 1$ sur $4$ mois alors que les paiements sont effectifs chaque mois $\implies$ rebinning à `0`).

---

### 🟠 Niveau 2 (`corrections_niveau2`) — Recalage de la codification `PAY_1 = 1` cohérence avec l'encours du mois
*Inclut l'intégralité des niveaux 0 et 1.*

* **Correction des incohérences `PAY_n = 1`** :
  * Si $\text{BILL\_AMT}_{n+1} \le 0 \implies \text{PAY}_n = \text{PAY}_{n+1}$.
  * Si $\text{BILL\_AMT}_{n+1} \le 0$ persistant $\implies \text{PAY}_n = 0$.

---

### 🔴 Niveau 3 (`corrections_niveau3`) — Recalage de la codification `PAY_1 = 1` par Ratio de Remboursement
*Inclut l'intégralité des niveaux précédents*
Analyse du ratio $R = \frac{\text{PAY\_AMT1}}{\text{BILL\_AMT2}}$ pour corriger les faux retards en $M-1$ (`PAY_1`) :
* **Si $R > 4$** :
  * Si $\text{PAY}_2 \le 0 \implies \text{PAY}_1 = \text{PAY}_2$.
  * Si $\text{PAY}_2 > 2 \implies \text{PAY}_1 = \text{PAY}_2$.
* **Si $R > 10$** :
  * Si $\text{PAY}_2 = 2 \implies \text{PAY}_1 = 0$.
* **Zone d'incertitude ($R < 4$)** :
  * Si $\text{PAY}_2 < 2 \implies \text{PAY}_1 = 1$ (Maintien de la codification 1 d'alerte).
  * Si $\text{PAY}_2 \ge 2 \implies \text{PAY}_1 = \text{PAY}_2$ (Non-résorption de la dette, retard initial maintenu).

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

### Résultats de ces expérimentations sur le dataset initial

S1 sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score Maître : 0.6881 | Recall  0.6310
🥈 RandomForest — Score Maître : 0.6876
🥉 LogisticRegression — Score Maître : 0.6492

**Résultats de `S2` :**  
🥇 RandomForest — Score Maître : 0.688 | Recall  0.6350
🥈 CatBoost — Score Maître : 0.6874
🥉 LogisticRegression — Score Maître : 0.6494
=> neutre, à essayer en combinaison avec un autre scenario pour vérifier son impact

**Résultats de `S3` :**  
🥇 CatBoost — Score Maître : 0.6934 | Recall  0.6218
🥈 RandomForest — Score Maître : 0.6915
🥉 LogisticRegression — Score Maître : 0.6613
Hausse généralisée des performances de tous les modèles et généralisation des bonnes performances à tous les modèles, plus aucun n'est à la traîne mais légère baisse du recall  
=> scénario conservé  

**Résultats de `S10` :** 
🥇 CatBoost — Score Maître : 0.6924 | 0.6231
🥈 RandomForest — Score Maître : 0.6918
🥉 LogisticRegression — Score Maître : 0.6607
Pas d'amélioration par rapport à `S3`
=> scénario écarté  

**Résultats de `S7` :**  
🥇 CatBoost — Score Maître : 0.6882 | Recall  0.6306
🥈 RandomForest — Score Maître : 0.6876
🥉 LogisticRegression — Score Maître : 0.6487
=> scénario mis de côté

**Résultats de `S8` :**  
🥇 RandomForest — Score Maître : 0.6924 | Recall  0.6233
🥈 CatBoost — Score Maître : 0.692
🥉 LogisticRegression — Score Maître : 0.6607
Aucune amélioration par rapport à `S3`  
=> scénario écarté

**Résultats de `S4` :**  
🥇 CatBoost — Score Maître : 0.6872 | Recall  0.6299
🥈 RandomForest — Score Maître : 0.6864
🥉 LogisticRegression — Score Maître : 0.6581
légère baisse des performances
=> scénario écarté

**Résultats de `S9` :**  
🥇 RandomForest — Score Maître : 0.6915 | Recall  0.621
🥈 CatBoost — Score Maître : 0.6911
🥉 LogisticRegression — Score Maître : 0.6669
Pas d'amélioration par rapport à `S3`
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score Maître : 0.6924 | Recall  0.6369
🥈 RandomForest — Score Maître : 0.6899
🥉 LogisticRegression — Score Maître : 0.6485
Très légère amélioration visible  
perte de performance constaté sur le jeu de tests inhabituel mais pas anormal
=> scénario conservé 

**Résultats de `S12` :**  
🥇 CatBoost — Score Maître : 0.6889 | Recall  0.6136
🥈 RandomForest — Score Maître : 0.687
🥉 LogisticRegression — Score Maître : 0.6559
Phénomène rare : meilleurs résultats sur le test que sur la validation  
Performances moins bonnes que S3 seul ou S11 seul
=> scénario écarté

**Résultats de `S13` :**  
🥇 CatBoost — Score Maître : 0.6572 | Recall  0.6058
🥈 RandomForest — Score Maître : 0.6543
🥉 LogisticRegression — Score Maître : 0.6164
Performances dégradées de 0.0309 et recall abaissé de 0.0252
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score Maître : 0.683 | Recall  0.6238
🥈 RandomForest — Score Maître : 0.6815
🥉 LogisticRegression — Score Maître : 0.646
Performances dégradées
=> scénario écarté

**Résultats de `S15` :**  
🥇 CatBoost — Score Maître : 0.6576 | Recall  0.6073
🥈 RandomForest — Score Maître : 0.6528
🥉 LogisticRegression — Score Maître : 0.6199
Performances dégradées de plus de 3 points sur le score
=> scénario écarté

**Conclusion**  
Pas de surapprentissage pour les scnéarii validés.  
Seul les scénari `S3` et `S11` apportent une réelle valeur ajoutée et répondent de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

### Résultats de ces expérimentations sur le dataset avec niveau 1 de corrections

*Passage à cv=3 dans GridSearchCV pour gagner du temps sur les 2 premiers entrainements rapides.*
`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score Maître : 0.6818 | Recall  0.6087
🥈 RandomForest — Score Maître : 0.6807
🥉 LogisticRegression — Score Maître : 0.652
Légère baisse des performances par rapport au niveau de correction 0, notamment 2 points de recall

**Résultats de `S2` :**  
🥇 CatBoost — Score Maître : 0.6817 | Recall  0.6081
🥈 RandomForest — Score Maître : 0.6805
🥉 LogisticRegression — Score Maître : 0.6534
Performances stables
=> à combiner éventuellement avec d'autres scénarii

**Résultats de `S3` :**  
🥇 RandomForest — Score Maître : 0.692 | Recall  0.6191
🥈 CatBoost — Score Maître : 0.6915
🥉 LogisticRegression — Score Maître : 0.6621
Améliorations de toutes les métriques
=> scénario conservé

**Résultats de `S10` :**  
🥇 RandomForest — Score Maître : 0.6913 | Recall  0.6174
🥈 CatBoost — Score Maître : 0.6897
🥉 LogisticRegression — Score Maître : 0.6602
Très légère régression par rapport à `S3` seul
=> scénario écarté

**Résultats de `S7` :**  
🥇 CatBoost — Score Maître : 0.681 | Recall  0.6109
🥈 RandomForest — Score Maître : 0.6805
🥉 LogisticRegression — Score Maître : 0.653
Performances équivalentes à `S1`
=> à combiner avec un autre scénario

**Résultats de `S8` :** 
🥇 RandomForest — Score Maître : 0.6908 | Recall  0.6191
🥈 CatBoost — Score Maître : 0.6906
🥉 LogisticRegression — Score Maître : 0.6601
Pas d'améliorations par rapport à `S3` seul
=> scénario écarté

**Résultats de `S4` :**  
🥇 RandomForest — Score Maître : 0.6789 | Recall  0.6040
🥈 CatBoost — Score Maître : 0.6774
🥉 LogisticRegression — Score Maître : 0.6573
Légère baisse des performances
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score Maître : 0.6867 | Recall  0.6148
🥈 RandomForest — Score Maître : 0.6841
🥉 LogisticRegression — Score Maître : 0.6537
baisse des performances légères
Phénomène notable : perte de recall sur le jeu de tests
=> scénario écarté

**Résultats de `S13` :**  
🥇 CatBoost — Score Maître : 0.6467 | Recall  0.5806
🥈 RandomForest — Score Maître : 0.6455
🥉 LogisticRegression — Score Maître : 0.6296
Performances dégradées de 0.0351 et recall abaissé de 0.0281
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score Maître : 0.6776 | Recall  0.6075
🥈 RandomForest — Score Maître : 0.6761
🥉 LogisticRegression — Score Maître : 0.6467
LR a un recall de 0.6516 !
performances légèrement moins bonnes
=> scénario écarté

**Résultats de `S15` :**  
🥇 CatBoost — Score Maître : 0.6472 | Recall  0.5771
🥈 RandomForest — Score Maître : 0.6373
🥉 LogisticRegression — Score Maître : 0.6298
Perte de plus de 3 points de performances et recall
=> scénario écarté

**Conclusion**  
Surapprentissage léger sur certains modèles.  
Seul le `scénario 3` apporte une réelle valeur ajoutée et répond de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

### Résultats de ces expérimentations sur le dataset avec niveau 2 de corrections

`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score Maître : 0.6807 | Recall  0.6097
🥈 RandomForest — Score Maître : 0.679
🥉 LogisticRegression — Score Maître : 0.649
Légère baisse des performances par rapport au dataset initial
Très légère baisse des performances et recall stable par rapport aux corrections de niveau 1

**Résultats de `S2` :**  
🥇 CatBoost — Score Maître : 0.6802 | Recall  0.6095
🥈 RandomForest — Score Maître : 0.679
🥉 LogisticRegression — Score Maître : 0.6485
Perfomances stables
=> scénario écarté

**Résultats de `S3` :**  
🥇 RandomForest — Score Maître : 0.6917 | Recall  0.6181
🥈 CatBoost — Score Maître : 0.6909 | 0.6195
🥉 LogisticRegression — Score Maître : 0.6595
Améliorations notables de toutes les performances
=> scénario conservé

**Résultats de `S10` :**  
🥇 CatBoost — Score Maître : 0.6913 | Recall  0.6210
🥈 RandomForest — Score Maître : 0.6906 | 0.6185
🥉 LogisticRegression — Score Maître : 0.6596
pas d'améliorataion par rapport à `S3` seul
=> scénario écarté

**Résultats de `S7` :**  
🥇 CatBoost — Score Maître : 0.6808 | Recall  0.6091
🥈 RandomForest — Score Maître : 0.679
🥉 LogisticRegression — Score Maître : 0.6484
Performances équivalentes à `S1`
=> scénario écarté

**Résultats de `S8` :** 
🥇 RandomForest — Score Maître : 0.6918 | Recall  0.6183
🥈 CatBoost — Score Maître : 0.6905
🥉 LogisticRegression — Score Maître : 0.6597
Pas d'amélioration par rapport à `S3` seul  
=> scénario écarté

**Résultats de `S4` :**  
🥇 CatBoost — Score Maître : 0.6787 | Recall  0.6063
🥈 RandomForest — Score Maître : 0.6779
🥉 LogisticRegression — Score Maître : 0.6533
Perte de performances
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score Maître : 0.687 | Recall  0.6158
🥈 RandomForest — Score Maître : 0.683
🥉 LogisticRegression — Score Maître : 0.65
Très légère amélioration des performances 
=> scénario conservé

**Résultats de `S12` :**  
🥇 CatBoost — Score Maître : 0.6875 | Recall  0.6169
🥈 RandomForest — Score Maître : 0.6842
🥉 LogisticRegression — Score Maître : 0.6528 
Performances similaires à `S11` mais inférieures à `S3`  
=> scénario écarté

**Résultats de `S13` :**  
🥇 CatBoost — Score Maître : 0.6467 | Recall  0.5806
🥈 RandomForest — Score Maître : 0.6451
🥉 LogisticRegression — Score Maître : 0.6295
Performances dégradées de 0.0340 et recall abaissé de 0.0291
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score Maître : 0.677 | Recall  0.6055
🥈 RandomForest — Score Maître : 0.675
🥉 LogisticRegression — Score Maître : 0.6409

**Résultats de `S15` :**  
🥇 CatBoost — Score Maître : 0.6472 | Recall  0.5814
🥈 RandomForest — Score Maître : 0.6402
🥉 LogisticRegression — Score Maître : 0.6295
Perte de plus de 3 points de performances et pres de 3 points de recall
=> scénario écarté

**Conclusion**  
Pas de surapparentissage.  
Seuls les `S3` et `S11` apportent une réelle valeur ajoutée et répondent de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.
Performances légèrement moins bonnes
=> scénario écarté

### Résultats de ces expérimentations sur le dataset avec niveau 3 de corrections

`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score Maître : 0.6808 | Recall  0.611
🥈 RandomForest — Score Maître : 0.6786
🥉 LogisticRegression — Score Maître : 0.6431
Un tout petit peu moins bon que le niveau de correction 0, équivalent aux niveau 1 et 2

**Résultats de `S2` :**  
🥇 CatBoost — Score Maître : 0.6789 | Recall  0.6093
🥈 RandomForest — Score Maître : 0.678
🥉 LogisticRegression — Score Maître : 0.6423
pas d'amélioration des performances  
=> scénario écarté

**Résultats de `S3` :**  
🥇 CatBoost — Score Maître : 0.6907 | Recall  0.6214
🥈 RandomForest — Score Maître : 0.6891
🥉 LogisticRegression — Score Maître : 0.66
Amélioration générales de toute les performances
=> scénario conservé

**Résultats de `S7` :**  
🥇 CatBoost — Score Maître : 0.6805 | Recall  0.6107
🥈 RandomForest — Score Maître : 0.6786
🥉 LogisticRegression — Score Maître : 0.6432
Pas d'amélioration par rapport à S1  
=> scénario écarté

**Résultats de `S8` :**  
🥇 CatBoost — Score Maître : 0.6908 | Recall  0.6212
🥈 RandomForest — Score Maître : 0.6891
🥉 LogisticRegression — Score Maître : 0.6599
Performances stables par rapport à `S3` seul
=> scénario à mettre de côté

**Résultats de `S4` :**  
🥇 CatBoost — Score Maître : 0.6793 | Recall  0.6093
🥈 RandomForest — Score Maître : 0.6763
🥉 LogisticRegression — Score Maître : 0.6516
pas d'amélioration des performances
=> scénario écarté

**Résultats de `S11` :**  
🥇 CatBoost — Score Maître : 0.6856 | Recall  0.6170
🥈 RandomForest — Score Maître : 0.6824
🥉 LogisticRegression — Score Maître : 0.6467
Amélioration des performances
Phénomène notable : baisse du recall de 2 points du recall sur le test
=> scénario conservé

**Résultats de `S12` :**  
🥇 CatBoost — Score Maître : 0.686 | Recall  0.6209
🥈 RandomForest — Score Maître : 0.6842
🥉 LogisticRegression — Score Maître : 0.6519
Phénomène notable : résultats meilleurs sur le jeu de tests
Très légère amélioration des performances par rapport à `S11`
Pas d'amélioration par rapport à `S3`
=> scénario conservé en lieu et place de `S11`

**Résultats de `S13` :**  
🥇 CatBoost — Score Maître : 0.6467 | Recall 0.5806
🥈 RandomForest — Score Maître : 0.6417
🥉 LogisticRegression — Score Maître : 0.6295 | Recall 0.6441
Performances dégradées de 0.0341 et recall abaissé de 0.0304
A noter un recall élevé pour LR
=> scécnario écarté pour la prédiction du risque à M

**Résultats de `S14` :**  
🥇 CatBoost — Score Maître : 0.6768 | Recall  0.6099
🥈 RandomForest — Score Maître : 0.6736
🥉 LogisticRegression — Score Maître : 0.6337
Performances légèrement dégradées
=> scénario écarté

**Résultats de `S15` :**  
🥇 CatBoost — Score Maître : 0.6472 | Recall  0.5814
🥈 RandomForest — Score Maître : 0.6405
🥉 LogisticRegression — Score Maître : 0.6281
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

Le jeu de données utilisé est celui de niveau de corrections 3.  
Ne sont traités que les clients avec un encours positif strict en M-1, et un plafond de crédit au maximum de 500 000 NT$. 

Je crée un pipeline simplifié
`S12_0` référence
🥇 CatBoost — Score Maître : 0.6865 | Recall  0.6196
🥈 RandomForest — Score Maître : 0.6771
🥉 LogisticRegression — Score Maître : 0.6515

`S12_1` : ajout des colonnes ratio_BILL_LIMITn = BILL_AMTn / LIMIT_BAL
Limite à 200% pour limiter le bruit de certaines valeurs aberrantes
Limite basse à 0% pour les encours non utilisés ou négatifs
🥇 CatBoost — Score Maître : 0.6877 | Recall  0.6211
🥈 RandomForest — Score Maître : 0.6791
🥉 LogisticRegression — Score Maître : 0.6507
=> nouveau scénario privilégié

`S12_2` : `S12_1` + 'AGE' décomposé en bins pertinents
L'âge n'est presque pas utilisé par les modèles pour prédire le défaut. Et pour cause, j'ai constaté que l'âge n'avait de sens que s'il est traité par tranches pour le mettre en corrélation avec le défaut de paiement.
Nouvelle Feature : tranches d'âge 'AGE_BUCKET' en remplacement de 'AGE'.  
🥇 CatBoost — Score Maître : 0.6866 | Recall  0.6175
🥈 RandomForest — Score Maître : 0.6773
🥉 LogisticRegression — Score Maître : 0.6505
=> scénario écarté

`S12_3` : `S12_1` + ajout des colonnes de ratio de paiement / encours utilisé
Elles indiquent au modèle indirectement si le client paie sa dette ou non, et quelle proportion, en évitant les NaN (si un client n'a pas de dette à M-1, on considère qu'il a payé 100%)
$\text{ratio\_PAY\_BILLn} = \begin{cases} \min\left(\max\left(\frac{\text{PAY\_AMTn}}{\text{BILL\_AMTn+1}}, \, 0.0\right), \, 2.0\right) & \text{si } \text{BILL\_AMTn+1} > 0 \\ 1.0 & \text{si } \text{BILL\_AMTn+1} \le 0 \end{cases}$
🥇 CatBoost — Score Maître : 0.6878 | Recall  0.6180
🥈 RandomForest — Score Maître : 0.6787
🥉 LogisticRegression — Score Maître : 0.6593
pas de gain, les informations étaient déjà présentes
=> scnéario écarté

`S12_4` : `S12_0` + substitution des colonnes PAY_AMTn et BILL_AMTn au profit des ratios de `S12_1` ration_BILL_LIMITn et `S12_3` ratio_PAY_BILLn
🥇 CatBoost — Score Maître : 0.686 | Recall  0.6150
🥈 RandomForest — Score Maître : 0.6773
🥉 LogisticRegression — Score Maître : 0.6505
pas de gain
=> scénario écarté

`S12_5` : `S12_1` + classer les clients par leur type d'usage (paiement différé total, crédit, autres)
pour ce faire, on va utiliser les colonnes ratio_PAY_AMTn_to_BILL_AMTn+1 pour regarder la médiane par client ratio_PAY_to_BILL_median et laisser les modèles faire leur propre découpage pour le lier au défaut de paiement
🥇 CatBoost — Score Maître : 0.6878 | Recall  0.6226
🥈 RandomForest — Score Maître : 0.6793
🥉 LogisticRegression — Score Maître : 0.6569
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
🥇 CatBoost — Score Maître : 0.6885 | Recall  0.6247
🥈 RandomForest — Score Maître : 0.6789
🥉 LogisticRegression — Score Maître : 0.6622
Cette variable a un impact légèrement positif sur les prédictions
=> nouveau scénario privilégié

`S12_7` : `S12_6` + Codification contentieux
J'ai détecté dans mon EDA un phénomène avec PAY_n = 2, il ne s'agit pas toujours d'un retard de 2 mois constaté
Créer une variable "flag" appelée 'CTX' qui est True si :
- PAY_n == 2 sur les 6 mois
- PAY_n == 2 et ((PAY_(n+1)>2) & (BILL_AMTn>0) & (PAY_AMTn == 0))
sinon False
🥇 CatBoost — Score Maître : 0.6875 | Recall  0.6198
🥈 RandomForest — Score Maître : 0.6772
🥉 LogisticRegression — Score Maître : 0.66
Ce premier résultat (moins bon que `S12_6` et surtout moins bon qu'attendu malgré une variable ultra discriminante implémentée) sans besoin de brider les modèles qui sont d'habitude en surapprentissage est un message, d'autant plus que les arbres n'utilisent pas cette variable : il y a peut etre un sous apprentissage par manque de profondeur. Je décide d'augmenter les fenêtres de paramètres pour ce scénario :  
🥇 CatBoost — Score Maître : 0.6875 | Recall  0.6198
🥈 RandomForest — Score Maître : 0.6846
🥉 LogisticRegression — Score Maître : 0.66
Aucune évolution donc pas la cause du problème. Probable que les modèles avaient déjà compris par eux-mêmes cette anomalie
Autre test pour vérifer un aspect étonnant (progression de 2 points de toutes les perf pour tous les modèles sur le jeu de test) : répartir équitablement les clients présumés 'CTX' :
🥇 CatBoost — Score Maître : 0.6872 | Recall  0.6221
🥈 RandomForest — Score Maître : 0.6848
🥉 LogisticRegression — Score Maître : 0.6562
Même si les résultats ne progressent pas (CTX n'est pas uniformisé dans les boucles du cross_validation), les résultats sur le jeu de tests surperforment encore davantage que précédemment, atteignant des scores jamais atteints auparavant. C'est la preuve que la variable 'CTX' a un impact fort. Ici, je suis confronté à un dilemne : conserver cette variable et l'intégrer de manière uniforme partout et sortir cette clientèle du circuit des clients sains, en entreprise j'aurais pu avoir ma réponse sur cette classification, mais je ne peux que supposer ici.
**71.27% des clients ayant un encours et étant taggé contentieux sont en défaut de paiement à M.**  
**Dans le jeu de données initial, 77.55% de taux de défaut de paiement pour les clients avec PAY_n = 2 sur les 6 mois**
Ces clients représentent 3.61% du jeu de données nettoyé. J'ai affaire à une anomalie dans les codifications de risques et de comportement des paiements et encours, couplé à un taux de défaut énorme





`Remonter cv dans GridSearchCV quand on approfondit les modèles`


## Problèmes rencontrés

### Redémarrage suite à un début d'encodage sur certaines colonnes  
J'ai testé :
1. sans encodage (les variables catégorielles étaient des nombres entiers)
2. lors de l'ajout de tranches d'âge, l'encodage est devenu obligatoire, je ne pouvais plus laisser des variables sans encodage, cela perturbait certaines de mes modèles testés, j'ai testé un OrdinalEncoder pour les tranches d'âge puis sur les PAY_n
3. j'ai testé un OneHotEncodeur sur les catégories non ordonnées et un OrdinalEncoder sur les catégories ordonnées
Après visualisation des résultats, le meilleur paramétrage était un encodage mixte : la solution `3`.  
J'ai également détecté que mon comparatif et ma matrice de confusion se faisait sur les résultats d'entrainement -> j'ai modifié pour que ce soit les performances de validation qui soient exposées et comparées au test => Forte diminution de la perte de recall
=> je vais relancer les 6 scnearii précédents pour tester vérifier si les résultats précédents se vérifiaient toujours