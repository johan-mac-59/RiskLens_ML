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
*Inclut l'intégralité du Niveau 0.*

* **Outliers montants** : Exclusion des $4$ observations présentant $\text{PAY\_AMT}_n > 1\,000\,000$.
* **Comptes inactifs** : Traitement des $860$ comptes sans activité ($\text{PAY\_AMT}_n = 0$ et $\text{BILL\_AMT}_n \le 0$ sur l'ensemble des $6$ mois).
* **Correction des incohérences `PAY_n = 1`** :
  * Si $\text{BILL\_AMT}_{n+1} \le 0 \implies \text{PAY}_n = \text{PAY}_{n+1}$.
  * Si $\text{BILL\_AMT}_{n+1} \le 0$ persistant $\implies \text{PAY}_n = 0$.
* **Anomalie isolée** : Correction manuelle du client `6783` ($\text{PAY} = 1$ sur $4$ mois alors que les paiements sont effectifs chaque mois $\implies$ rebinning à `0`).

---

### 🟠 Niveau 2 (`corrections_niveau2`) — Recalage de la codification `PAY_1 = 1` par Ratio de Remboursement
*Inclut l'intégralité des Niveaux 0 et 1.*

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

### 🔴 Niveau 3 (`corrections_niveau3`) — Repositionnement des Soldes Positifs
*Inclut l'intégralité des Niveaux 0, 1 et 2.*

Correction des codifications `-2` (*compte inactif*) sur les comptes présentant un encours réel :

* Si $\text{PAY}_n = -2$ et $\text{BILL\_AMT}_{n+1} > 0 \implies \text{PAY}_n = -1$.
* Si $\text{PAY}_6 = -2$ et $\text{PAY}_5 = -1 \implies \text{PAY}_6 = -1$.

---

## 2. Scénarios d'Expérimentation Transversaux

Au sein de chaque niveau de correction, des scénarios autonomes sont appliqués de façon identique :

* **`S1` (Baseline)** : Aucun réencodage supplémentaire par rapport au niveau de correction actif.
* **`S2` (Plafonnement des impayés)** : Clamping des retards sévères ($\text{PAY}_n > 2 \implies 2$).
* **`S3` (Filtrage encours actif)** : Restriction de la population aux clients avec $\text{BILL\_AMT1} > 0$.
* **`S4` (Simplification clients à Jour)** : Regroupement des statuts sans retard ($\text{PAY}_n \in \{-2, -1\} \implies 0$).
* **`S5` (Simplification plafonnement des impayés et clients à jours)** : S2 + S4

---

