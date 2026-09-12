*Traduit en français par Gemini | les schémas sont dans le rapport original*

# Comparaison des techniques de minage de données pour la précision prédictive de la probabilité de défaut des clients de cartes de crédit

**I-Cheng Yeh** et **Che-hui Lien**  
*Expert Systems with Applications* 36 (2009) 2473–2480

---

## Résumé
Cette recherche examine le cas des défauts de paiement des clients à Taïwan et compare la précision prédictive de la probabilité de défaut entre six méthodes de minage de données. Du point de vue de la gestion des risques, le résultat de la précision prédictive de la probabilité de défaut estimée a plus de valeur que le résultat binaire de classification (clients solvables ou non solvables). La véritable probabilité de défaut étant inconnue, cette étude présente une nouvelle méthode, la « Méthode de Lissage par Tri » (*Sorting Smoothing Method* ou SSM), pour estimer la véritable probabilité de défaut. 

En prenant la véritable probabilité de défaut comme variable dépendante ($Y$) et la probabilité de prédiction du défaut comme variable indépendante ($X$), les résultats de la régression linéaire simple ($Y = A + BX$) montrent que le modèle de prévision produit par les réseaux de neurones artificiels possède le coefficient de détermination le plus élevé ; son ordonnée à l'origine ($A$) est proche de zéro et son coefficient de régression ($B$) est proche de un. Par conséquent, parmi les six techniques de minage de données, le réseau de neurones artificiels est la seule qui puisse estimer avec précision la véritable probabilité de défaut.

**Mots-clés :** Banque ; Réseau de neurones ; Probabilité ; Minage de données

---

## 1. Introduction
Ces dernières années, les émetteurs de cartes de crédit à Taïwan ont fait face à une crise de la dette liée aux liquidités et aux cartes de crédit, les impayés devant atteindre leur pic au troisième trimestre de 2006 (Chou, 2006). Afin d'augmenter leur part de marché, les banques émettrices de cartes à Taïwan ont surémis des cartes de crédit et de liquidités à des demandeurs non qualifiés. Parallèlement, la plupart des détenteurs de cartes, indépendamment de leur capacité de remboursement, ont surutilisé leur carte de crédit pour la consommation et ont accumulé de lourdes dettes. Cette crise a porté un coup à la confiance dans le crédit à la consommation et constitue un défi majeur tant pour les banques que pour les détenteurs de cartes.

Dans un système financier bien développé, la gestion des crises intervient en aval et la prévision des risques en amont. L'objectif principal de la prévision des risques est d'utiliser des informations financières (états financiers d'entreprises, enregistrements de transactions et de remboursements des clients, etc.) pour prédire la performance des entreprises ou le risque de crédit des clients individuels, et ainsi réduire les dommages et l'incertitude.

De nombreuses méthodes statistiques, incluant l'analyse discriminante, la régression logistique, le classifieur de Bayes et les $k$ plus proches voisins, ont été utilisées pour développer des modèles de prévision des risques (Hand & Henley, 1997). Avec l'évolution de l'intelligence artificielle et de l'apprentissage automatique, les réseaux de neurones artificiels et les arbres de classification ont également été employés pour prévoir le risque de crédit (Koh & Chan, 2002 ; Thomas, 2000). Le risque de crédit désigne ici la probabilité d'un retard dans le remboursement du crédit accordé (Paolo, 2001).

Du point de vue du contrôle des risques, l'estimation de la probabilité de défaut est plus significative que la classification des clients en résultats binaires (risqué / non risqué). Par conséquent, la question de savoir si la probabilité de défaut estimée par les méthodes de minage de données peut représenter la « véritable » probabilité de défaut constitue un problème important. Prévoir la probabilité de défaut est un défi pour les praticiens et les chercheurs, qui nécessite des études approfondies (Baesens et al., 2003 ; Desai et al., 1996 ; Hand & Henley, 1997 ; Jagielska & Jaworski, 1996 ; Lee et al., 2002 ; Rosenberg & Gleit, 1994 ; Thomas, 2000).

La véritable probabilité de défaut étant inconnue, cette étude propose une nouvelle méthode, la « Méthode de Lissage par Tri » (SSM), pour déduire la probabilité réelle de défaut et apporter des réponses aux deux questions suivantes :
1. Existe-t-il une différence de précision de classification entre les six techniques de minage de données ?
2. La probabilité de défaut estimée par les méthodes de minage de données peut-elle représenter la véritable probabilité de défaut ?

Dans la section suivante, nous passons en revue les six techniques de minage de données et leurs applications au scoring de crédit. Ensuite, en utilisant des données réelles de risque de crédit de porteurs de cartes à Taïwan, nous comparons leur précision de classification. La section 4 est dédiée aux performances prédictives de la probabilité de défaut. Enfin, la section 5 présente les conclusions.

---

## 2. Revue de littérature

### 2.1. Techniques de minage de données
À l'ère de l'explosion de l'information, chaque entreprise produit et collecte de vastes volumes de données au quotidien. Découvrir des connaissances utiles dans les bases de données et transformer l'information en résultats exploitables constitue un défi majeur. Le minage de données est le processus d'exploration et d'analyse, par des moyens automatiques ou semi-automatiques, de grandes quantités de données afin de découvrir des motifs et des règles significatifs (Berry & Linoff, 2000). Actuellement, le minage de données est un outil indispensable dans les systèmes d'aide à la décision.

Les avantages et inconvénients des six techniques de minage de données évaluées sont les suivants (Han & Kamber, 2001 ; Hand et al., 2001 ; Paolo, 2003 ; Witten & Frank, 1999) :

#### 2.1.1. Classifieurs des $K$ plus proches voisins (KNN)
Les classifieurs KNN reposent sur l'apprentissage par analogie. Face à un échantillon inconnu, le classifieur KNN recherche dans l'espace des motifs les $K$ voisins les plus proches. La proximité est définie par une mesure de distance. L'échantillon inconnu se voit attribuer la classe la plus fréquente parmi ses voisins.
*   **Avantage :** Pas besoin d'établir un modèle prédictif avant la classification.
*   **Inconvénients :** Ne produit pas de formule explicite de probabilité de classification ; la précision dépend fortement de la mesure de distance et du paramètre $K$.

#### 2.1.2. Régression logistique (RL)
La régression logistique est un cas particulier des modèles de régression linéaire, adapté aux variables de réponse binaires. 
*   **Avantage :** Produit une formule probabiliste simple de classification.
*   **Inconvénients :** Ne gère pas correctement les problèmes non linéaires et les effets d'interaction entre variables explicatives.

#### 2.1.3. Analyse discriminante (DA)
Aussi connue sous le nom de règle de Fisher, l'analyse discriminante est une alternative à la régression logistique reposant sur l'hypothèse d'une distribution normale multivariée des variables explicatives pour chaque classe, avec une matrice de variance-covariance commune.
*   **Avantages et inconvénients :** Similaires à ceux de la régression logistique.

#### 2.1.4. Classifieur bayésien naïf (NB)
Fondé sur le théorème de Bayes, il suppose l'indépendance conditionnelle des attributs par rapport à la classe.
*   **Avantage :** Simplifie considérablement les calculs et fournit une justification théorique.
*   **Inconvénient :** L'hypothèse d'indépendance conditionnelle est souvent violée en pratique en raison de corrélations entre variables.

#### 2.1.5. Réseaux de neurones artificiels (RNA / ANN)
Les réseaux de neurones utilisent des équations mathématiques non linéaires pour modéliser des relations complexes entre entrées et sorties via un processus d'apprentissage (réseaux de rétropropagation ou *back-propagation*).
*   **Avantage :** Traitent aisément les effets non linéaires et interactifs des variables explicatives.
*   **Inconvénient :** Ne permettent pas d'obtenir une formule probabiliste simple et transparente.

#### 2.1.6. Arbres de classification (CT)
Structure arborescente où chaque nœud interne représente un test sur un attribut, chaque branche un résultat, et chaque feuille une classe.
*   **Avantages :** Fournissent des règles de classification simples et gèrent la non-linéarité.
*   **Inconvénients :** Sensibilité élevée aux données observées (une modification mineure peut altérer toute la structure de l'arbre) et complexité algorithmique séquentielle.

---

## 3. Précision de classification parmi les techniques de minage de données

### 3.1. Description des données
L'étude a exploité les données de paiement d'octobre 2005 d'une grande banque émettrice de cartes de crédit à Taïwan. Sur un total de **25 000 observations**, **5 529 observations (22,12 %)** correspondent à des porteurs de cartes en défaut de paiement. La variable dépendante est binaire : défaut de paiement ($Oui = 1$, $Non = 0$). 

Vingt-trois variables explicatives ($X_1$ à $X_{23}$) ont été retenues :
*   **$X_1$ :** Montant du crédit accordé (en dollars taïwanais - NTD), incluant le crédit personnel et familial.
*   **$X_2$ :** Sexe ($1 =$ homme, $2 =$ femme).
*   **$X_3$ :** Niveau d'éducation ($1 =$ cycle supérieur, $2 =$ université, $3 =$ lycée, $4 =$ autre).
*   **$X_4$ :** Situation maritale ($1 =$ marié(e), $2 =$ célibataire, $3 =$ autre).
*   **$X_5$ :** Âge (en années).
*   **$X_6$ à $X_{11}$ :** Historique des paiements passés (d'avril à septembre 2005). L'échelle de mesure est : $-1 =$ paiement effectué à temps ; $1 =$ retard d'un mois ; $2 =$ retard de deux mois ; ... ; $8 =$ retard de huit mois ; $9 =$ retard de neuf mois et plus.
*   **$X_{12}$ à $X_{17}$ :** Montant des relevés de facturation (d'avril à septembre 2005, en NTD).
*   **$X_{18}$ à $X_{23}$ :** Montant des paiements précédents (d'avril à septembre 2005, en NTD).

Les données ont été divisées aléatoirement en deux groupes : l'un pour l'entraînement du modèle, l'autre pour la validation. 
Le taux d'erreur s'avérant insuffisant et insensible dans un contexte déséquilibré (où 87,88 % des clients sont solvables), cette étude utilise **le ratio de surface dans le graphique de lift** (*Lift Chart*) comme critère d'évaluation de la précision de classification, défini par :

$$\text{Ratio de surface} = \frac{\text{Aire entre la courbe du modèle et la courbe de référence (baseline)}}{\text{Aire entre la courbe théoriquement optimale et la courbe de référence}}$$

### 3.2. Résultats de classification
Le Tableau 1 résume les performances en termes de taux d'erreur et de ratio de surface pour les données d'entraînement et de validation.

**Tableau 1 : Précision de la classification**
| Méthode | Taux d'erreur (Entraînement) | Taux d'erreur (Validation) | Ratio de surface (Entraînement) | Ratio de surface (Validation) |
| :--- | :---: | :---: | :---: | :---: |
| **K plus proches voisins (KNN)** | 0,18 | 0,16 | 0,68 | 0,45 |
| **Régression logistique (LR)** | 0,20 | 0,18 | 0,41 | 0,44 |
| **Analyse discriminante (DA)** | 0,29 | 0,26 | 0,40 | 0,43 |
| **Bayésien naïf (NB)** | 0,21 | 0,21 | 0,47 | 0,53 |
| **Réseaux de neurones (ANN)** | 0,19 | 0,17 | 0,55 | **0,54** |
| **Arbres de classification (CT)** | 0,18 | 0,17 | 0,48 | 0,536 |

*Analyse :* Sur l'échantillon de validation (mesurant la capacité de généralisation), les **réseaux de neurones artificiels (ANN)** obtiennent la meilleure performance avec le ratio de surface le plus élevé ($0,54$) et un taux d'erreur faible ($0,17$).

---

## 4. Précision prédictive de la probabilité de défaut

### La Méthode de Lissage par Tri (*Sorting Smoothing Method* - SSM)
Pour estimer la véritable probabilité de défaut, la méthode SSM fonctionne en deux étapes :
1. Trier les données de validation par ordre croissant selon la probabilité prédite.
2. Appliquer la formule de lissage :

$$P_i = \frac{Y_{i-n} + Y_{i-n+1} + \cdots + Y_{i-1} + Y_i + Y_{i+1} + \cdots + Y_{i+n-1} + Y_{i+n}}{2n + 1}$$

Où :
*   $P_i$ = probabilité réelle de défaut estimée au $i$-ème rang des données de validation ;
*   $Y_i$ = variable binaire du risque de défaut réel ($1$ = survenu, $0$ = non survenu) ;
*   $n$ = nombre de données prises en compte pour le lissage (dans cette étude, $n = 50$).

### Évaluation par régression linéaire ($Y = A + BX$)
En traçant le diagramme de dispersion (probabilité prédite en abscisse $X$, probabilité réelle lissée en ordonnée $Y$), on évalue la qualité du modèle via le coefficient de détermination ($R^2$), l'ordonnée à l'origine ($A$) et le coefficient de régression ($B$). Un modèle idéal possède un $R^2$ proche de $1$, un coefficient $B$ proche de $1$ et une ordonnée $A$ proche de $0$.

**Tableau 2 : Synthèse de la régression linéaire entre probabilité réelle et probabilité prédite**
| Méthode | Coefficient de régression ($B$) | Ordonnée à l'origine ($A$) | Coefficient de détermination ($R^2$) |
| :--- | :---: | :---: | :---: |
| **K plus proches voisins** | 0,770 | 0,0522 | 0,876 |
| **Régression logistique** | 1,233 | -0,0523 | 0,794 |
| **Analyse discriminante** | 0,837 | -0,1530 | 0,659 |
| **Bayésien naïf** | 0,502 | 0,0901 | 0,899 |
| **Réseaux de neurones (ANN)** | **0,998** | **0,0145** | **0,965** |
| **Arbres de classification** | 1,111 | -0,0276 | 0,278 |

---

## 5. Conclusion
Cette étude a examiné six techniques de classification en minage de données et introduit la **Méthode de Lissage par Tri (SSM)** pour estimer la véritable probabilité de défaut.

1. **Précision de classification :** Le ratio de surface s'est révélé être un critère beaucoup plus sensible que le taux d'erreur sur des données déséquilibrées. Les réseaux de neurones artificiels surclassent les autres méthodes.
2. **Précision prédictive de la probabilité :** Les réseaux de neurones démontrent des performances exceptionnelles avec un $R^2$ de **0,9647** (proche de 1), une ordonnée à l'origine de **0,0145** (proche de 0) et un coefficient de régression de **0,9981** (proche de 1). 

Par conséquent, **le réseau de neurones artificiels est la seule technique dont la probabilité prédite représente fidèlement la véritable probabilité de défaut**. Du point de vue de la gestion des risques bancaires, l'utilisation des réseaux de neurones doit être privilégiée par rapport à la régression logistique classique pour l'évaluation quantitative du risque de crédit.