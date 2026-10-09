# Hypothèses et conclusions du projet

Ce document garde la trace des hypothèses formulées pendant le projet, des preuves qui les soutiennent ou les contredisent, et des conclusions qu'on peut en tirer. Il sert à deux choses : proposer de nouveaux tests, et préparer la conclusion du projet.

**Statuts** : ✅ confirmée (mesurée dans un notebook, avec la méthode du projet) · 🟡 probable (plusieurs indices concordants, pas de test dédié) · 🔎 à tester · ⚙️ décision de méthode.

**Sources des chiffres** : chaque chiffre renvoie à son notebook. Les contrôles faits à la volée pendant la discussion du 07/10/2026 ont été recalculés dans `lab_ML/controles_cible.ipynb` (notebook descriptif, aucun modèle entraîné) : ils y renvoient.

---

## 1. La cible et ses limites

### H1. Le plafond des modèles vient de la cible, pas des modèles ni des variables ✅

Les scores plafonnent hors contentieux, quelles que soient les variables, les réglages ou les modèles.
- Scénarios : score décisionnel F2 entre 0,482 et 0,489 au rappel minimal de 60 % (`ml_0` à `ml_15`), précision des défauts prédits autour de 27 %, ROC AUC autour de 0,71 (`tableau_ML.md`).
- Modèles poussés sans contrainte de surapprentissage : aucun ne dépasse `ml_11` (`diagnostic_capacite.ipynb`).
- Réglages élargis : aucun effet sur le meilleur modèle (`ml_14` face à `ml_12`, 0,485 → 0,485).
- Colonnes supplémentaires : dans le bruit, même mesurées finement (`duel_fin_ml14_ml15.ipynb` : +0,0026 sur 50 plis, t corrigé = 0,79).
- Petite population reprise : dans le bruit (`ml_16` : +0,0003, t = 0,33).

### H2. Une part des défauts est imprévisible avec ces données ✅

- Environ un tiers des défauts de la partie d'analyse (248 sur 771) ne sont signalés par aucun des 4 modèles de `ml_14`, au rappel de 60 % (`analyse_defauts_manques.ipynb`).
- Ces défauts manqués ressemblent aux bons clients non signalés sur 8 indicateurs sur 9 ; les modèles leur donnent la même probabilité qu'aux bons clients (0,31 contre 0,29).
- Aucun profil à part n'en ressort : aucune colonne n'a pu en être tirée.
- Les modèles s'accordent : 410 défauts sur 771 sont détectés par les 4 modèles à la fois, 248 par aucun. **Combiner plusieurs modèles (vote, moyenne des probabilités) est donc une piste écartée** : elle ne ferait pas apparaître les défauts qu'aucun ne voit.

### H3. La cible `dpnm` suit le statut posé par la banque plutôt qu'un défaut de paiement observé 🟡

La définition exacte de `dpnm` n'est pas documentée (`contexte.md`). Plusieurs indices vont dans ce sens :
- **ne rien devoir protège à peine du défaut** : les clients sans dette en septembre font défaut à 18,2 % (1 649 clients, niveau 5), contre 21,7 % en moyenne ; sans aucune dette sur les six mois, 24 % (25 clients) (`controles_cible.ipynb`) ;
- **au contentieux, payer ne change rien** : les clients au contentieux qui ont payé en août et en septembre font défaut à 70,7 % (1 617 clients), autant que l'ensemble du contentieux (70,5 %) (`controles_cible.ipynb`) ;
- **une codification de retard posée sur une dette nulle annonce presque autant de défauts qu'un vrai retard** : jeu de base, `PAY_1` ≥ 2 avec une facture d'août nulle ou négative : 63,5 % de défaut (63 clients), contre 69,6 % pour tous les `PAY_1` ≥ 2 (`controles_cible.ipynb`) ;
- **même neutralisés au niveau 5, ces retards restent un signal** : faux retards (`FAUX_CODAGE`) 33,3 % de défaut (45 clients), retards sur compte endormi (`SURVEILLANCE_RECENTE`) 50,3 % (179 clients) (`controles_cible.ipynb`).

**Conséquence** : le défaut tel qu'il est codé ne laisse aucune porte de sortie à un client que la banque a étiqueté, quel que soit son comportement de paiement. C'est probablement la source principale du plafond (H1) et des défauts imprévisibles (H2).

**Tests possibles** : taux recalculés avec leurs effectifs dans `controles_cible.ipynb` (fait) ; vérifier si le défaut d'octobre se lit dans une codification d'octobre que l'on n'a pas (la cible serait alors la codification du mois suivant).

### H4. Les codifications de la banque ont du retard sur les paiements ❌ non confirmée

Un client qui recommence à payer peut garder une codification de retard pendant un ou deux mois (convention du projet : un paiement de régularisation peut être enregistré avec un mois de décalage). Si les modèles « voyaient » ces clients, ce serait par leurs paiements (`PAY_AMTn`), pas par leurs `PAY_n`.
- **Résultat** (`essai_jeu_corrige_deux_populations.ipynb`, sections 3 et 4) : au contentieux, les paiements pèsent peu dans ce que trouvent les modèles (ce sont surtout les factures et la démographie), et aucun modèle, même sans les `PAY_n`, ne distingue assez nettement les clients qui paieront pour les sortir. Au contentieux, les clients qui paient font défaut autant que les autres (H3).
- Le retard des codifications existe sans doute dans les données, mais il ne se traduit pas en clients repérables par leurs paiements.

### H15. L'échantillon a été sélectionné, et la sélection rend la tâche plus difficile qu'elle ne l'est pour une banque 🟡

- **Un taux de défaut irréaliste** : 22 % des clients sont en défaut ; aucune banque ne tiendrait longtemps à ce niveau, même en pleine crise. L'étude ne décrit pas comment l'échantillon a été tiré : les défauts y sont probablement sur-représentés, et les taux affichés décrivent l'échantillon, pas la banque (appliqué tel quel à un vrai portefeuille, le modèle surestimerait le risque).
- **Biais de sélection** : si l'échantillon a écarté une grande partie des clients ordinaires, qui paient sans incident, les modèles ont appris à départager des clients plus risqués et plus semblables entre eux que dans la réalité.
- **Effet de dilution, en ordre de grandeur** : pour que le portefeuille ne compte plus que 5 % de défauts, il faudrait 5,3 fois plus de bons clients. Si ces clients ajoutés sont des payeurs ordinaires, le modèle les range en risque faible : au seuil de 60 % des défauts hors contentieux, rien ne change pour les clients signalés, mais le modèle ne fait plus 1,7 fois mieux que le hasard, il fait 8 fois mieux ; le risque faible passe de 9,7 % à 1,5 % de défaut (Streamlit, page 8.4, calculé en direct).
- **Hypothèse invérifiable avec les données seules** : il faudrait connaître la façon dont l'échantillon a été tiré (section 7).

---

## 2. Ce que portent les données

### H5. Sur l'ensemble des clients, les codifications dominent parce qu'elles repèrent le contentieux ✅

- Sur les 30 000 clients du jeu de base, les `PAY_n` portent 71 à 86 % de la perte de précision moyenne quand on les mélange, et d'abord `PAY_1` (`essai_jeu_de_base.ipynb`, section 5) ; même constat au niveau 5 (76 à 88 %, `essai_jeu_corrige.ipynb`).
- Avec un seul modèle sur le jeu de base et la règle marginale à 1 pour 1, 77,9 % des clients signalés sont au contentieux, et 96,2 % du contentieux est signalé (97,0 % de ses défauts détectés) ; hors contentieux, seuls 9,9 % des défauts sont détectés (`controles_cible.ipynb`, section 5).

### H6. Hors contentieux, le comportement du client porte le signal au moins autant que les codifications ✅

Sur les clients du train ML, plis des scénarios, score décisionnel F2 au rappel de 60 % (section 6 des essais) :

| Essai, meilleur modèle | Complet | Sans les `PAY_n` (montants, plafond, démographie) | `PAY_n` seuls |
|---|---|---|---|
| Jeu de base (niveau 0) | 0,485 | 0,482, dans le bruit face à `ml_4` (0,484) | 0,455, perte |
| Jeu corrigé (niveau 5) | 0,486 | 0,480, dans le bruit | 0,461, perte |

**Réponse partielle à la problématique** : oui, le comportement du client explique une partie du défaut, indépendamment des codifications de la banque ; cette partie reste modeste (environ un client signalé sur quatre réellement en défaut, au rappel de 60 %).

### H7. Le nettoyage n'améliore pas le score ; son apport est la cohérence des données ✅ (indicatif)

- Le jeu de base complet, sans nettoyage ni colonne construite, atteint le plateau des scénarios (0,485 face à 0,484 pour `ml_4`, dans le bruit).
- Du niveau 0 au niveau 5, les résultats bougent très peu (ROC AUC 0,784 dans les deux essais).
- Les deux essais n'ont ni le même périmètre ni les mêmes plis : l'écart mêle le changement de périmètre et les corrections des `PAY_n`.
- **Piste écartée (09/10)** : un essai au niveau 4 du nettoyage (`cleaned4` : mêmes clients que le niveau 5, avant les corrections de codification du contentieux) isolerait l'effet de ces corrections. Elles ne modifient les codifications que de 346 clients sur 28 851, soit 1,2 % (comparaison de `cleaned4` et `cleaned5`), et l'écart attendu serait plus petit que l'incertitude de la mesure ; les deux essais ne montrent déjà que des écarts minimes. L'essai n'est donc pas lancé (Streamlit, page 8.5).

### H8. Les colonnes construites aident la régression logistique, sans que le gain soit démontrable ✅

- La régression logistique gagne avec les colonnes de `ml_11` (gain réel sur 5 plis face à `ml_4`, +0,007), mais ce gain ne résiste pas à la mesure fine (`duel_fin_ml14_ml15.ipynb` : +0,0054, 40 plis sur 50, t corrigé = 1,65).
- Elle profite aussi de petits groupes que les arbres ne peuvent pas isoler : par exemple `EDUCATION` = 4, 306 clients du train avec 6,5 % de défaut (`controles_cible.ipynb`).

### H9. Plus de variables ne fait pas un meilleur modèle : à score égal, le plus simple ✅

- Version finale : `ml_14` (21 variables, aucune donnée démographique), à égalité avec `ml_11` et `ml_15` (54 variables).
- Le meilleur score parmi des candidats à égalité est biaisé vers le haut (piège du gagnant) : l'avance de `ml_15` passe de +0,004 sur 5 plis à +0,0026 sur 50 plis.

---

## 3. Le contentieux

### H10. La règle « tout le contentieux en défaut » est la seule décision défendable avec ces données ✅

- Le contentieux à M (définition 2) fait défaut à 70,5 % (3 004 clients du niveau 5).
- Avec une tolérance métier stricte (on ne sort un client du contentieux que s'il a au moins 9 chances sur 10 d'être sain), tous les modèles, dans les trois variantes, gardent la quasi-totalité du contentieux en défaut ; ils y trient à peine mieux que le hasard (ROC AUC d'environ 0,55 à 0,61) (`essai_jeu_corrige_deux_populations.ipynb`, section 3). Même constat pour le groupe `PAY_1` ≥ 2 du jeu de base (`essai_jeu_de_base_deux_populations.ipynb`).
- Rien dans les données ne distingue les clients du contentieux qui paieront (H3).
- Hors contentieux, la règle « 1 pour 1 » ne signale qu'environ 2 % des clients et n'attrape qu'environ 5 % des défauts (217 sur 4 155), avec environ 51 % de précision ; le meilleur modèle hors contentieux, avec les seules 23 colonnes d'origine, fait jeu égal avec `ml_14` sur les clients du train ML (0,486 contre 0,485).

### H12. La règle du contentieux ne prédit pas mieux que la codification de la banque : match nul sur le score ✅

Sur les mêmes 28 851 clients du niveau 5 (`essai_jeu_de_base_deux_populations.ipynb`, section 6) :

| Stratégie | Séparation | Défauts détectés | Précision | Fausses alertes | Taux d'erreur | Ratio d'aire |
|---|---|---|---|---|---|---|
| Règle seule | Banque (`PAY_1` ≥ 2, jeu de base) | 2 169 (34,6 %) | 69,5 % | 951 | 0,175 | 0,324 |
| Règle seule | Contentieux (définition 2, jeu corrigé) | 2 117 (33,8 %) | 70,5 % | 887 | 0,175 | 0,318 |
| Règle + ML | Banque | 2 464 (39,3 %) | 66,6 % | 1 237 | 0,175 | 0,565 |
| Règle + ML | Contentieux | 2 334 (37,2 %) | 68,0 % | 1 098 | 0,175 | 0,565 |

- Les deux séparations se recouvrent presque entièrement : 2 886 des 3 004 clients au contentieux ont aussi `PAY_1` ≥ 2.
- La codification de la banque attrape un peu plus de défauts, au prix d'un peu plus de fausses alertes : à la marge, ces clients supplémentaires ne sont en défaut qu'environ une fois sur deux. Taux d'erreur et ratio d'aire identiques.
- **La valeur de la définition 2 n'est pas le score** : elle est justifiée et explicable (deux retards d'affilée, faux retards neutralisés), là où `PAY_1` ≥ 2 retient aussi des retards isolés et des faux retards. La comparaison mêle la règle et le nettoyage : elle répond à « tout le travail fait-il mieux que la codification de la banque ? ».

### H13. Toutes les approches tombent sur la même courbe de niveaux de risque ✅

Niveaux de risque (règle, puis haut risque jusqu'à 30 % de rappel, puis risque modéré jusqu'à 60 %), sur les 27 202 clients communs au périmètre du ML (`comparatif_global/niveaux_de_risque_global.ipynb`, classement hors pli ou par le modèle final) :

| Approche | Règle seule | + haut risque | + risque modéré |
|---|---|---|---|
| Version finale `ml_14` | 35,4 % des défauts, précision 70,5 % | 54,9 %, 56,4 % | 74,3 %, 38,8 % |
| Contentieux + ML, 23 colonnes | 35,4 %, 70,5 % | 55,7 %, 56,3 % | 73,4 %, 39,3 % |
| Contentieux + ML sans les `PAY_n` | 35,4 %, 70,5 % | 55,2 %, 53,4 % | 73,4 %, 38,4 % |
| Banque (`PAY_1` ≥ 2) + ML, 23 colonnes | 36,3 %, 69,5 % | 54,2 %, 58,4 % | 71,3 %, 41,4 % |
| Banque + ML sans les `PAY_n` | 36,3 %, 69,5 % | 53,3 %, 56,2 % | 71,6 %, 40,3 % |

- **Le travail sur les variables n'a pas déplacé la courbe** : la version finale fait comme les modèles sur les 23 colonnes brutes, à chaque niveau (H1, H7).
- **La séparation du contentieux et celle de la banque se valent** : la banque signale un peu moins de clients au niveau modéré, attrape un peu moins de défauts avec une précision un peu plus haute : un autre point de la même courbe (H12).
- **Le comportement seul fait presque aussi bien** : sans aucune codification, le modèle ne perd qu'environ 3 points de précision sur le haut risque, rien sur la part des défauts. Une fois le contentieux mis à part par la règle, les montants portent l'essentiel de ce qui est prévisible (H6).
- **Évaluation finale** : sur le test, jamais vu, les taux par niveau sont les mêmes que sur le train hors pli (haut risque 42,0 % contre 41,2 %, modéré 21,3 % contre 20,4 %, faible 9,5 % contre 9,8 %) : la courbe est celle du portefeuille (`evaluation_finale_test.ipynb`).
- **Confirmé sur des clients jamais vus (08/10)** : sur les 5 441 clients des démonstrations (test du ML et 20 % du contentieux du périmètre), qu'aucun des deux systèmes n'a vus, le système du projet (règle du contentieux, puis `ml_14`) et un CatBoost sur les 23 variables d'origine (sans nettoyage ni règle, chaque client noté par un modèle de pli qui ne l'a pas vu, `lab_ML/demo_ML/creation_demo_3.ipynb`) font **jeu égal**. Le modèle brut est réglé pour trouver la même part des défauts que le projet à chaque palier ; les précisions ne s'écartent que de 2,3 points au plus, dans un sens puis dans l'autre : contentieux seul 70,5 % contre 69,9 % ; + très haut risque 67,2 % contre 66,0 % ; + haut risque 56,8 % contre 59,1 % ; + risque modéré 39,5 % contre 37,8 %. ROC AUC 0,787 contre 0,790 (Streamlit, page 8.1, calculé en direct). L'apport du projet n'est pas le score mais un système défendable à score égal : une règle lisible, aucune donnée démographique (le modèle brut se sert du genre, de l'âge, des études et du statut marital), des corrections justifiées.
- **Cinq niveaux depuis le 07/10** : découpage présenté sur Streamlit (page 6.4) : le haut risque est coupé en deux par une borne ajoutée après la lecture du test (`tableau_ML.md`, section 3) : très haut risque, 10 % des défauts, 51,3 % de défaut ; haut risque, de 10 à 30 %, 37,7 %. Les chiffres ci-dessus restent ceux de l'évaluation, à quatre niveaux.

### H14. Les corrélations de l'EDA sont réelles, mais elles distinguent des groupes, pas des individus ✅

- L'EDA montre de vrais écarts de taux de défaut entre groupes (type d'usage, utilisation du plafond, retards, démographie) ; le modèle les retrouve : du risque faible (environ 10 % de défaut) au haut risque (environ 41 %), un écart de 1 à 4, stable du train au test (H13) ; avec le très haut risque (tête de liste, environ 51 %), un écart de 1 à 5.
- Mais même un groupe à 41 % de défaut compte une majorité de clients qui paient, et la tête de liste elle-même (51 %) en compte la moitié : les corrélations rangent bien les clients par niveau de risque, sans désigner lequel fera défaut. Fort entre groupes, faible au client près : le cas classique du risque de crédit.
- Les colonnes construites n'ont pas amélioré le score du meilleur modèle. Leur effet dépend du modèle (le SVM profite de l'historique des retards et du résumé des codifications, la régression logistique de toutes les colonnes ensemble), sans dépasser le bruit en meilleur contre meilleur. Deux raisons possibles, impossibles à départager : l'information était déjà dans les montants et les codifications d'origine, que le modèle combine lui-même ; ou le signal (comportement inhabituel, rupture) était trop rare, trop faible ou sans lien avec la cible. Les corrélations de l'EDA se sont montrées moins fortes qu'espéré, et la cible n'étant pas documentée, le défaut reste en partie inexpliqué. Les colonnes construites restent utiles pour **décrire** le risque d'un groupe. La démographie a un lien réel mais faible et redondant avec le comportement : l'élagage l'a retirée sans perte.
- **Réponse à la problématique** : le comportement du client explique une partie du défaut, à l'échelle des groupes ; il ne suffit pas à prédire le défaut de chaque client avec certitude.

### H11. Le contentieux gonfle les scores des jeux qui le contiennent ✅

- ROC AUC d'environ 0,78 sur les jeux avec contentieux, contre environ 0,71 hors contentieux.
- Hors contentieux, sur les mêmes clients, le jeu de base fait jeu égal avec les scénarios (H6) : l'écart venait du contentieux, facile à repérer.

---

## 4. Décisions de méthode issues de ces réflexions ⚙️

- **Rappel minimal de 60 % dans les scénarios** : choix de départ, qui juge tous les modèles au même point. À ce point, la précision marginale (les derniers clients signalés) n'est que d'environ 18 %, à peine plus que le hasard (16 %) (18,5 %) ; garder une précision de 50 % ne permettrait de détecter que 12,0 % des défauts (`controles_cible.ipynb`, section 6).
- **Comparatif global** :
  - critère des réglages : la précision moyenne, qui juge le tri sur tous les rappels ;
  - seuil de décision par la **règle marginale** : signaler un client tant que les derniers signalés valent la peine (gain net « défauts détectés − tolérance × bons clients signalés »). C'est la règle de décision à coûts fixés : elle ne dépend pas du taux de défaut, seulement du coût des erreurs ;
  - **le F2 maximal est écarté** : il s'arrête quand la précision marginale tombe à F2 / 5, soit environ 1 défaut pour 7 bons clients ; avec 22 % de défauts, signaler tout le monde donne déjà un F2 d'environ 0,59 ;
  - **un plancher sur la précision moyenne est écarté** : il laisse passer, à la marge, des clients bien moins souvent en défaut que le plancher ;
  - **tolérance par population, fixée par le coût de l'erreur** : 1 bon client signalé pour 1 défaut hors contentieux ; au contentieux, on ne sort un client que s'il a au moins 9 chances sur 10 d'être sain, car sortir à tort un client qui ne paiera pas abandonne une créance.
- **Un seul modèle, une seule règle** : sans séparation, le contentieux n'existe pas ; le modèle unique répond à « qui paiera ou ne paiera pas ? », avec la même exigence pour tous. L'écart avec les stratégies séparées mesure l'effet de la séparation dans son ensemble.
- **Puissance de la comparaison** : sur 5 plis, le bruit des gains pli par pli est d'environ 0,006 en score décisionnel F2 (environ 620 défauts par pli) ; « dans le bruit » veut dire « pas démontré », pas « moins bon ». Pour un écart proche de ce bruit, mesurer plus finement (validation croisée répétée, test t corrigé de Nadeau et Bengio) plutôt que changer la règle après coup.
- **Règle de verdict à améliorer** : quand deux versions sont identiques, des écarts de 0,0001 peuvent donner un « gain réel » artificiel (vu dans `ml_14`) ; exiger aussi un gain minimal (par exemple 0,001) serait une nouvelle version de la méthode, non décidée.

---

## 5. Face à l'étude d'origine (Yeh et Lien, 2009)

- L'étude ne publie ni ROC AUC ni rappel : seulement un taux d'erreur et un ratio d'aire (Tableau 1, p. 2477), sur un seul découpage. Son ratio d'aire vaut exactement 2 × ROC AUC − 1.
- **Qualité du tri** : légèrement meilleure ici. Ratio d'aire de 0,567 (jeu de base) et 0,568 (jeu corrigé) pour CatBoost, contre 0,54 pour leur meilleur modèle, le réseau de neurones.
- **Le système du projet** (règle du contentieux, puis `ml_14`), sur les 5 441 clients des démonstrations jamais vus : ratio d'aire de 0,57 (ROC AUC 0,787, environ 0,79), contre 0,54 (0,77) : défi relevé, de peu (Streamlit, page 8.2, calculé en direct).
- **Taux d'erreur** : au même niveau, pas meilleur. 0,180 (jeu de base) et 0,174 (jeu corrigé) à la règle marginale, contre 0,17 pour leur réseau de neurones et 0,16 pour leur KNN.
- **Sans modèle**, la règle « tout le contentieux en défaut » donne déjà un taux d'erreur de 0,175 sur le niveau 5 (`essai_jeu_corrige_deux_populations.ipynb`, section 6) ; sur le fichier brut, la règle de la banque (`PAY_1` ≥ 2) donne 0,180, et règle + ML : taux d'erreur 0,180, ratio d'aire 0,564, **sur le même périmètre que l'étude** (`essai_jeu_de_base_deux_populations.ipynb`, section 5).
- L'article contient des incohérences (25 000 observations annoncées pour 30 000 dans le fichier ; 22,12 % de défauts puis 87,88 % de clients sans risque).

**À dire dans la conclusion, avant tout chiffre** : la comparaison avec l'étude ne peut pas être exacte, pour trois raisons.
- **Leur objectif n'était pas le nôtre.** L'étude cherche d'abord à **bien estimer la probabilité de défaut** (sa méthode de lissage, *Sorting Smoothing Method*, et la régression entre probabilité estimée et « vraie » probabilité, R² de 0,965 pour le réseau de neurones) et à **bien trier** les clients (ratio d'aire). Elle ne cherche pas à **détecter** un maximum de défauts à un seuil choisi : elle ne publie ni rappel ni précision, et son taux d'erreur suppose un seuil qu'elle ne décrit pas. Nos modèles sont réglés pour détecter (précision au rappel de 60 %, ou règle marginale) et pondèrent les défauts : leurs probabilités sont décalées vers le haut, donc mal calibrées au sens de l'étude.
- **Les modèles ont progressé depuis.** Le réseau de neurones de l'étude est un réseau à rétropropagation de 2006-2007 : l'étude est publiée en 2009, mais menée avant (son texte parle du pic des impayés « attendu » au troisième trimestre de 2006, et l'article est enregistré par l'éditeur dès la fin de 2007, doi:10.1016/j.eswa.2007.12.020) ; les modèles de boosting d'arbres utilisés ici (CatBoost, comme XGBoost et LightGBM) sont apparus après (années 2016 à 2018), avec la validation croisée et la recherche automatique de réglages devenues courantes. Que notre meilleur modèle trie un peu mieux (ratio d'aire) est attendu ; que l'écart reste faible confirme que la limite vient des données (H1).
- **Nos traitements diffèrent des leurs, sans que l'on connaisse les leurs en détail** : un seul découpage chez eux (proportions non précisées, environ la moitié des clients en validation d'après leurs courbes de gain), une validation croisée à 5 plis ici ; réglages, mise à l'échelle et traitement du déséquilibre non décrits chez eux ; ici, logarithme des montants, pondération des défauts, contrôle du surapprentissage, retrait du contentieux (version finale) ou séparation par la règle (comparatif global).

---

## 6. Ce que je referais autrement (leçons de méthode)

La méthode a été rigoureuse (aucune règle ni seuil optimisé sur la cible, test lu une seule fois et confirmant la validation, tout tracé et reproductible) et le résultat de fond n'aurait sans doute pas changé. Le chemin aurait pu être plus court :
1. **Estimer tôt le bruit qui reste dans le périmètre retenu.** Le bruit visible de la cible (des clients sans dette comptés en défaut) a été écarté dès le départ, par le périmètre à encours positif. Ce qui n'a été mesuré qu'à la fin, c'est la part de défauts imprévisibles **restant** dans ce périmètre (environ un tiers, H2) : l'estimer dès les premiers scénarios aurait annoncé le plafond.
2. **Calculer ce que la comparaison peut détecter avant d'ajouter les colonnes une à une.** Avec 5 plis, le bruit des gains était d'environ 0,006 en score décisionnel F2 : presque tous les ajouts sont tombés dans le bruit. Commencer par le scénario complet puis élaguer, ou mesurer finement (validation croisée répétée) dès le départ, aurait été plus rapide.
3. **Comparer sur une mesure sans seuil, décider du point de fonctionnement à la fin.** Rejugés sur la précision moyenne, aucun scénario ne dépasse le socle `ml_0` (23 variables d'origine) ; la version finale est même un peu en dessous, dans le bruit (`controles_cible.ipynb`, section 7 ; réserve : modèles réglés sur une autre mesure). Les essais réglés directement sur la précision moyenne tombent sur la même courbe (H13). Comparer ainsi dès le départ aurait montré plus tôt que les colonnes construites n'apportent rien au score. La règle de décision (rappel minimal, règle marginale, niveaux de risque) se choisit ensuite, avec la banque ; la règle « 1 pour 1 », qui signale très peu de clients hors contentieux, aurait été une mauvaise mesure de comparaison (trop bruitée).
4. **Refaire une exploration courte sur la population du ML, une fois le contentieux retiré.** L'exploration (partie 4) a été menée sur tout le portefeuille, contentieux compris ; sans lui, une partie des liens s'efface (clients actifs S12, taux de défaut, avec / sans contentieux) : comptant 14,3 % / 14,2 % contre crédit lent 25,0 % / 16,1 % (presque effacé) ; utilisation du plafond < 30 % contre 90 % et plus : 17,1 % / 14,3 % contre 26,3 % / 18,8 % (réduit) ; plafond ≤ 50 000 contre 200 000 à 500 000 NT$ : 32,1 % / 24,0 % contre 13,1 % / 10,3 % (se maintient : 2,5 puis 2,3 fois) ; aucun retard contre au moins un mois en retard : 11,6 % / 11,6 % contre 46,8 % / 32,6 % (diminue, de 4,0 à 2,8 fois, mais reste le plus fort). Les liens qui tiennent (plafond, retards) sont ceux que garde la version finale ; ceux qui s'effacent (type d'usage, utilisation du plafond) n'ont rien apporté aux scénarios. Ce contrôle, fait avant les scénarios, aurait annoncé quelles colonnes avaient une chance d'aider (contrôle du 07/10, page Streamlit 6.5, calculé en direct sur le dataset).
5. **Appliquer la règle « à score égal, le plus simple » au choix du modèle, pas seulement aux variables.** Dans la version finale `ml_14` (21 variables), les quatre modèles étaient à égalité (CatBoost 0,485, régression logistique 0,482, dans le bruit) ; CatBoost a été désigné parce qu'il était en tête, ce qui revient au piège du gagnant (H9). À égalité, la régression logistique, plus simple et plus explicable (un poids lisible par variable, justifiable devant la gestion des risques), aurait été le choix cohérent. Choix fixé avant la lecture du test, non revu ensuite (sur le test : 0,494 contre 0,487, toujours dans l'incertitude) ; dit aussi sur Streamlit (page 6.6).
6. **La calibration**, objectif principal de l'étude d'origine, n'a pas été traitée : mise de côté (probabilité personnalisée par client : piste, section 8).

## 7. Ce qui manque pour aller plus loin (ouverture)

- **La définition exacte de `dpnm`** : défaut de paiement observé ou statut posé par la banque (H3).
- **Les vrais encours** : `BILL_AMT` est le montant du relevé, qui ne serait pas toujours la dette réelle (certains défauts chez des clients sans dette affichée le laissent penser). Avec l'encours réel, on saurait si les clients « sans dette » l'étaient vraiment, et si leur défaut est du bruit de la cible ou une dette invisible dans les relevés.
- **La façon dont l'échantillon a été tiré** : avec environ un client sur cinq en défaut, il ne ressemble pas à un portefeuille réel ; savoir quels clients ont été retenus dirait si la sélection a rendu la tâche plus difficile (H15).
- **La vraie liste des clients en incident hors circuit normal** (recouvrement, contentieux) : elle permettrait de valider la définition 2 du contentieux (clients retrouvés, manqués, ajoutés à tort) et de séparer le défaut « administratif » du vrai défaut de paiement, là où se cache probablement le tiers de défauts imprévisibles (H2).

**Conclusion provisoire** : on a tiré de ces données ce qu'elles contiennent, et on sait mesurer ce qu'elles ne contiennent pas. Nettoyer davantage les variables selon des règles métier transformerait le jeu en notre propre lecture ; recoder la cible changerait la question (les modèles prédiraient notre définition du défaut). La suite logique dépasse ce jeu de données : obtenir les données manquantes ci-dessus.

---

## 8. Tests à mener (issus de ces hypothèses)

| Test | Hypothèse | État |
|---|---|---|
| Recalculer dans un notebook les contrôles rapides (taux de défaut des clients sans dette, des clients du contentieux qui paient, des retards posés sans dette, part du contentieux parmi les signalés) | H3, H5 | fait (07/10) : `lab_ML/controles_cible.ipynb` |
| Lire le contentieux dans `essai_jeu_corrige_deux_populations.ipynb` : variante « sans les `PAY_n` », importance par famille | H4, H10 | fait (07/10) |
| Comparer la séparation du contentieux à celle de la banque (`PAY_1` ≥ 2), sur les clients communs | H12 | fait (07/10) : match nul |
| Ajouter la stratégie « un seul ML » aux deux synthèses (cellules d'enregistrement des essais à un seul modèle, puis synthèse) | H10, H12 | fait (07/10) |
| Essai au niveau 4 du nettoyage (avant les corrections de codification du contentieux) pour isoler l'effet de ces corrections | H7 | écarté (09/10) : écart attendu sous l'incertitude de la mesure |
| Règle de verdict avec un gain minimal | méthode | à décider |
| Mesurer la calibration à la manière de l'étude (lissage, régression probabilité estimée / « vraie », R²) sur les probabilités hors pli, éventuellement après calibration des modèles : comparaison sur leur objectif principal | section 5 | piste, non lancé |
