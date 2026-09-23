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
=> neutre, à essayer en combinaison d'un autre scénario pour vérifier son impact

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
=> neutre, à essayer en combinaison avec un autre scenario pour vérifier son impact

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
🥇 CatBoost — Score Maître : 0.6872 | Recall  0.6184
🥈 RandomForest — Score Maître : 0.6824
🥉 LogisticRegression — Score Maître : 0.6541
Très légère amélioration des performances mais surapprentissage léger sur certains modèles  
baisse des performances et du recall notable sur le jeu de tests
=> à combiner avec un autre scénario

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
pas d'amélioration
=> à tester en combinaison avec un autre scénario

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

**Conclusion**  
Pas de surapparentissage.  
Seuls les `S3` et `S11` apportent une réelle valeur ajoutée et répondent de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

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
=> à combiner avec un autre scénario pour voir s'il apporte quelque chose en plus

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


**Conclusion**  


### Conclusion sur les différents niveaux de nettoyage et leurs scénarii




---

## 3. Features

1. L'âge n'est presque pas utilisé par les modèles pour prédire le défaut. Et pour cause, j'ai constaté que l'âge n'avait de sens que s'il est traité par tranches pour le mettre en corrélation avec le défaut de paiement.
Nouvelle Feature : tranches d'âge en remplacement de 'AGE'



## Redémarrage suite à un début d'encodage sur certaines colonnes  
J'ai testé :
1. sans encodage (les variables catégorielles étaient des nombres entiers)
2. lors de l'ajout de tranches d'âge, l'encodage est devenu obligatoire, je ne pouvais plus laisser des variables sans encodage, cela perturbait certaines de mes modèles testés, j'ai testé un OrdinalEncoder pour les tranches d'âge puis sur les PAY_n
3. j'ai testé un OneHotEncodeur sur les catégories non ordonnées et un OrdinalEncoder sur les catégories ordonnées
Après visualisation des résultats, le meilleur paramétrage était un encodage mixte : la solution `3`.  
J'ai également détecté que mon comparatif et ma matrice de confusion se faisait sur les résultats d'entrainement -> j'ai modifié pour que ce soit les performances de validation qui soient exposées et comparées au test => Forte diminution de la perte de recall
=> je vais relancer les 6 scnearii précédents pour tester vérifier si les résultats précédents se vérifiaient toujours



S8 : ajout des colonnes ratio_BILL_LIMIT = BILL_AMTn / LIMIT_BAL si BILL_AMTn>=0 SINON =0
Limite à 200% pour limiter le bruit de certaines valeurs aberrantes

S9 : classer les clients par leur type d'usage (paiement différé total, crédit, autres)
pour ce faire, on va utiliser les colonnes ratio_PAY_to_BILL_AMTn pour regarder la médiane par client ratio_PAY_to_BILL_median :
- si ratio_median == 0 : client en impayé chronique codifié 'impayé chronique'
- si 0 < ratio_median <= 3 : client en paiement partiel codifié 'insuffisant'
- si 3 < ratio_median <= 10 : client en paiement correct usage crédit codifié 'credit'
- si 10 < ratio_median <= 90 : client en paiement partiel du total, usage mixte ou présentant des incidents sur son paiement total codifié 'mixte'
- si ratio_median > 90 : client en paiement comptant codifié 'comptant'
- si pas de donnée : 'autre'

S10 : indicateur d'activation récente du crédit (entre M-1 et M-4 sans encours sur tous les mois précédent)  
on va regarder l'activation des comptes sur la période et les taguer comme suit :
- compte toujours actif : 0
- actif depuis m-4 : 4
- actif depuis m-3 : 3
- actif depuis m-2 : 2
- actif depuis m-1 : 1
inclut S9  
intéret : Ajouter un flag pour les clients récents qui peuvent avoir un 'ratio_PAY_to_BILL_median' trompeur  
De plus, cela ajoute un indicateur aux modèles : client récent, activation de compte, réactivation de compte, sortie de contentieux  

S11 : S10 + S8 ?


S?? : Codification contentieux
'CTX' = True si :
- PAY_n == 2 sur les 6 mois
- PAY_n == 2 et ((PAY_(n+1)>2) & (BILL_AMTn>0) & (PAY_AMTn == 0))
sinon False






Remonter cv dans GridSearchCV quand on approfondit les modèles