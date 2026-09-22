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

### 🟠 Niveau 2 (`corrections_niveau2`) — Recalage de la codification `PAY_1 = 1` par Ratio de Remboursement
*Inclut l'intégralité des niveaux 0 et 1.*

* **Correction des incohérences `PAY_n = 1`** :
  * Si $\text{BILL\_AMT}_{n+1} \le 0 \implies \text{PAY}_n = \text{PAY}_{n+1}$.
  * Si $\text{BILL\_AMT}_{n+1} \le 0$ persistant $\implies \text{PAY}_n = 0$.

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
* **`S7`(Plafonnement léger des impayés)** : Clamping des retards sévères ($\text{PAY}_n >3 \implies 3$).
* **`S8` (Filtrage encours actif + plafonnement léger des impayés)** : S3 + S7
* **`S9` (Filtrage encours actif + Simplification clients à Jour)** : S3 + S4
* **`S10` (Simplification plafonnement des impayés + Filtrage encours actif)** : S2 + S3


### Méthodologie

Afin d'évaluer les performances de telle ou telle modification du jeu de données ou d'une variable et d'avoir un score unique souverain dans mes décisions, j'utilise 2 métriques d'optimisation :
- ROC AUC indirectement utilisé par I-Cheng Yeh et Che-hui Lien pour évaluer les performances de leurs modèles
- F2 score très adapté au milieu bancaire qui pénalise assez fortement la non détection de cas positifs
J'applique la moyenne de ces 2 métriques pour chaque modèle pour obtenir un score moyen que j'uniformise à toutes mes expérimentations

### Résultats de ces expérimentations sur le dataset initial

S1 sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 RandomForest — Score Maître : 0.6876 |  Recall  0.6338
🥈 CatBoost — Score Maître : 0.6871
🥉 LogisticRegression — Score Maître : 0.6501

**Résultats de `S2` :**  
🥇 RandomForest — Score Maître : 0.688 | Recall  0.6350
🥈 CatBoost — Score Maître : 0.6874
🥉 LogisticRegression — Score Maître : 0.6494
=> neutre, à essayer en combinaison avec un autre scenario pour vérifier son impact

**Résultats de `S3` :**  
🥇 CatBoost — Score Maître : 0.6926 | Recall  0.6231
🥈 RandomForest — Score Maître : 0.6924
🥉 LogisticRegression — Score Maître : 0.6613
CatBoost légèrement moins bon que RandomForest mais meilleur recall
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
PAs d'amélioration par rapport à `S3`
=> scénario écarté

**Conclusion**  
Pas de surapparentissage.  
Seul le `scénario 3` apporte une réelle valeur ajoutée et répond de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

### Résultats de ces expérimentations sur le dataset avec niveau 1 de corrections

*Passage à cv=3 dans GridSearchCV pour gagner du temps sur les 2 premiers entrainements rapides.*
`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score Maître : 0.6809 - Recall  0.6105
🥈 RandomForest — Score Maître : 0.6805
🥉 LogisticRegression — Score Maître : 0.6536
Légère baisse des performances par rapport au niveau de correction 0, notamment 2 points de recall

**Résultats de `S2` :**  
🥇 CatBoost — Score Maître : 0.6809 | Recall  0.6099
🥈 RandomForest — Score Maître : 0.6806
🥉 LogisticRegression — Score Maître : 0.6534
Performances stables
=> à combiner avec d'autres scénarii

**Résultats de `S3` :**  
🥇 CatBoost — Score Maître : 0.6914 | Recall  0.6206
🥈 RandomForest — Score Maître : 0.6908
🥉 LogisticRegression — Score Maître : 0.6599
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

**Conclusion**  
Pas de surapparentissage.  
Seul le `scénario 3` apporte une réelle valeur ajoutée et répond de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.

### Résultats de ces expérimentations sur le dataset avec niveau 2 de corrections

`S1` sert de base pour mesurer la progression éventuelle des scenarii suivants :
🥇 CatBoost — Score Maître : 0.6795 | Recall  0.6105
🥈 RandomForest — Score Maître : 0.6781
🥉 LogisticRegression — Score Maître : 0.6419
Légère baisse des performances par rapport au dataset initial
Très légère baisse des performances et recall stable par rapport aux corrections de niveau 1

**Résultats de `S2` :**  
🥇 CatBoost — Score Maître : 0.6789 | Recall  0.6093
🥈 RandomForest — Score Maître : 0.678
🥉 LogisticRegression — Score Maître : 0.6423
pas d'amélioration
=> à tester en combinaison avec un autre scénario

**Résultats de `S3` :**  
🥇 CatBoost — Score Maître : 0.6906 | Recall  0.6216
🥈 RandomForest — Score Maître : 0.6898
🥉 LogisticRegression — Score Maître : 0.6591
Amélioration notables de toutes les performances
=> scénario conservé

**Résultats de `S10` :**  
🥇 CatBoost — Score Maître : 0.6907 | Recall  0.6220
🥈 RandomForest — Score Maître : 0.6896
🥉 LogisticRegression — Score Maître : 0.6587
pas d'améliorataion par rapport à `S3` seul
=> scénario écarté

**Résultats de `S7` :**  
🥇 CatBoost — Score Maître : 0.6801 | Recall  0.6115
🥈 RandomForest — Score Maître : 0.6781
🥉 LogisticRegression — Score Maître : 0.6413
Performances équivalentes à `S1`
=> à combiner avec un autre scénario

**Résultats de `S8` :** 
🥇 CatBoost — Score Maître : 0.6901 | Recall  0.6206
🥈 RandomForest — Score Maître : 0.6898
🥉 LogisticRegression — Score Maître : 0.6582
pas d'amélioration par rapport à `S3` seul
=> scénario écarté

**Résultats de `S4` :**  
🥇 CatBoost — Score Maître : 0.6774 | Recall  0.6063
🥈 RandomForest — Score Maître : 0.6763
🥉 LogisticRegression — Score Maître : 0.6504
Perte de performances
=> scénario écarté

**Conclusion**  
Pas de surapparentissage.  
Seul le `scénario 3` apporte une réelle valeur ajoutée et répond de surcroit à une réalité métier. Les autres simplifications effacent des couches d'informations utiles aux modèles pour prédire le futur défaut de paiement.


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