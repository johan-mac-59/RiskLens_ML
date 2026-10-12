# Hypothèses et conclusions du projet

Ce document garde la trace des hypothèses formulées pendant le projet, des preuves qui les soutiennent ou les contredisent, et des conclusions qu'on peut en tirer. Il sert à deux choses : proposer de nouveaux tests, et préparer la conclusion du projet.

**Statuts** : ✅ confirmée (mesurée dans un notebook, avec la méthode du projet) · 🟡 probable (plusieurs indices concordants, pas de test dédié) · 🔎 à tester · ⚙️ décision de méthode.

**Sources des chiffres** : chaque chiffre renvoie à son notebook (dossier `lab_ML/` : version finale `ml_17`, `evaluation_finale_test.ipynb`, `analyse_defauts_manques.ipynb`, `eda_population_ml.ipynb` ; dossier `lab_ML/comparatif_global/` : essais hors scénarios), ou à une page du site, où il est recalculé en direct.

**Vocabulaire** : les deux **populations des règles métier** sont la population en incident à M (deux codifications de retard d'affilée, ou une seule de 3 ou plus) et le retard imminent ; elles sont déclarées en défaut de paiement sans modèle. Les **autres clients**, ceux qui ont une dette en septembre et un plafond de 500 000 NT$ au plus, sont confiés au machine learning.

---

## 1. La cible et ses limites

### H1. Le plafond des modèles vient des données, pas des modèles ni des variables ✅

Sur les autres clients, les scores plafonnent quels que soient les variables, les réglages ou les modèles.
- Scénarios `ml_0` à `ml_17`, six modèles (cinq dans `ml_17`) : score décisionnel F2 entre 0,433 et 0,453 au taux de rappel minimal de 60 %, précision des défauts prédits autour de 22 %, ROC AUC autour de 0,69 (`tableau_ML.md`).
- Réglages élargis : aucun effet sur le meilleur modèle (`ml_17` : CatBoost 0,451, contre 0,450 dans `ml_16`).
- Un modèle sur les 23 variables d'origine, sans nettoyage ni colonne construite, fait jeu égal avec `ml_17` sur les mêmes clients et les mêmes plis (0,450 contre 0,451, dans le bruit ; `essai_jeu_de_base.ipynb`, section 6).
- Sur le test, jamais vu, le plafond tient : ROC AUC 0,675 contre 0,690 en validation, précision des défauts prédits 21,9 % contre 22,6 % (`evaluation_finale_test.ipynb`, section 2).

### H2. Une part des défauts de paiement est imprévisible avec ces données ✅

- Dans la partie d'analyse (un quart du train du ML, tiré avant l'analyse : 4 491 clients, 620 défauts de paiement), 154 défauts, soit 24,8 %, ne sont signalés par aucun des cinq modèles de `ml_17`, chacun à son seuil du taux de rappel minimal ; 305 le sont par les cinq à la fois (`analyse_defauts_manques.ipynb`, section 2).
- Ces défauts manqués ressemblent aux bons clients non signalés plus qu'aux défauts détectés, sur 6 indicateurs sur 9 : aucun mois en retard (médiane), tous ont payé en septembre, plafond médian de 185 000 NT$ ; les modèles leur donnent une probabilité moyenne de 0,21, proche de celle des bons clients non signalés (0,19), loin de celle des défauts détectés (0,35) (sections 3 et 4).
- Aucun profil à part n'en ressort : aucune colonne n'a pu en être tirée.
- Les modèles s'accordent : la moitié des défauts (305 sur 620) sont trouvés par les cinq modèles, un quart par aucun. **Combiner plusieurs modèles (vote, moyenne des probabilités) est donc une piste écartée** : elle ne ferait pas apparaître les défauts qu'aucun ne voit.

### H3. La cible `dpnm` suit le statut posé par la banque plutôt qu'un défaut de paiement observé 🟡

La définition exacte de `dpnm` n'est pas documentée (`contexte.md`). Deux indices vont dans ce sens (`eda_population_ml.ipynb`, sections 5 et 6 ; page 6.5 du site, calculé en direct) :
- **ne rien devoir protège à peine du défaut de paiement** : les clients sans dette en septembre font défaut à 18,2 % (1 649 clients), contre 21,7 % pour tous les clients nettoyés ; sans aucune dette sur les six mois, 24,0 % (25 clients) ;
- **en incident, payer ne change rien** : sur le train du découpage commun, les 3 019 clients en incident à M font défaut à 58,9 % ; ceux qui ont payé en août et en septembre, à 60,8 % (1 007 clients) ; ceux qui n'ont payé ni l'un ni l'autre, à 68,0 % (350). Le groupe le plus bas, l'incident court (un ou deux mois), reste à 41,5 % (698).

**Conséquence** : le défaut de paiement tel qu'il est noté ne laisse presque aucune porte de sortie à un client que la banque a étiqueté, quel que soit son comportement de paiement. C'est probablement une source importante du plafond (H1) et des défauts imprévisibles (H2).

**Test possible** : vérifier si le défaut d'octobre se lit comme une codification d'octobre que l'on n'a pas (la cible serait alors le jugement de la banque sur la facture suivante).

### H4. L'échantillon a été sélectionné, et la sélection rend la tâche plus difficile qu'elle ne l'est pour une banque 🟡

- **Un taux de défaut de paiement irréaliste** : 22 % des clients sont en défaut de paiement ; aucune banque ne tiendrait longtemps à ce niveau, même en pleine crise. L'étude ne décrit pas comment l'échantillon a été tiré : les défauts y sont probablement sur-représentés, et les taux affichés décrivent l'échantillon, pas la banque (appliqué tel quel à un vrai portefeuille, le modèle surestimerait le risque).
- **Biais de sélection** : si l'échantillon a écarté une grande partie des clients ordinaires, qui paient sans incident, les modèles ont appris à départager des clients plus risqués et plus semblables entre eux que dans la réalité.
- **Effet de dilution, en ordre de grandeur** : si l'on ajoute assez de payeurs ordinaires pour ramener le portefeuille à 5 % de défaut de paiement, et que le modèle les range en risque faible, les clients signalés ne changent pas, mais le modèle fait bien plus nettement mieux que le hasard, et le risque faible devient presque sans défaut (page 8.4 du site, calculé en direct).
- **Hypothèse invérifiable avec les données seules** : il faudrait connaître la façon dont l'échantillon a été tiré (section 7).

---

## 2. Ce que portent les données

### H5. Sur l'ensemble des clients, les codifications dominent parce qu'elles repèrent les populations à risque ✅

- Sur les 30 000 clients du jeu de base, les codifications (`PAY_n`) portent 71 à 86 % de la perte de précision moyenne quand on les mélange, et d'abord `PAY_1` (`essai_jeu_de_base.ipynb`, section 5) ; même constat sur le jeu corrigé (niveau 3 du nettoyage, `essai_jeu_corrige.ipynb`, section 5).
- Un seul modèle sur tous les clients du niveau 3, sans séparation, trouve 2 527 défauts de paiement à la règle « 1 pour 1 » : 2 480 sont dans les deux populations des règles (98 %), 47 seulement parmi les autres clients, sur 3 401 (`essai_jeu_corrige_deux_populations.ipynb`, section 8).

### H6. Hors des règles, le comportement du client porte l'essentiel du signal ✅

Sur les 17 967 clients du train du ML, plis des scénarios, score décisionnel F2 au taux de rappel minimal de 60 %, meilleur modèle (`essai_jeu_de_base.ipynb` et `essai_jeu_corrige.ipynb`, section 6) :

| Essai | Complet (23 variables) | Sans les `PAY_n` (montants, plafond, démographie) | `PAY_n` seuls |
|---|---|---|---|
| Jeu de base (niveau 0) | 0,450 | 0,440 | 0,410 |
| Jeu corrigé (niveau 3) | 0,450 | 0,440 | 0,416 |
| Version finale `ml_17` (21 variables) | 0,451 | | |

- **Sans aucune codification**, la perte face à `ml_17` est réelle mais petite (−0,012 et −0,011) ; **avec les seules codifications**, elle est nette (−0,04).
- La version finale ne garde des codifications qu'un comportement tagué, le nombre de mois en retard (`CUMUL_INCIDENT`, lu sur les codifications corrigées) ; retirer les codifications brutes n'a rien changé au score (`ml_3`, page 6.3).
- Sur tout le périmètre, avec les niveaux de risque, un modèle sans aucune codification trouve 78,1 % des défauts de paiement jusqu'au risque modéré, avec 35,5 % de précision, contre 78,8 % et 36,4 % pour la version finale (`niveaux_de_risque_global.ipynb` ; page 8.1).

**Réponse partielle à la problématique** : une fois les populations à risque mises à part, le comportement du client porte l'essentiel de ce qui est prévisible ; cette part reste modeste (environ un client signalé sur cinq réellement en défaut de paiement, au taux de rappel minimal de 60 %).

### H7. Le nettoyage n'améliore pas le score ; son apport est la cohérence des données ✅ (indicatif)

- Le jeu de base complet, sans nettoyage ni colonne construite, fait jeu égal avec `ml_17` sur les clients du ML (0,450 contre 0,451, dans le bruit) ; le jeu corrigé (niveau 3) aussi (0,450).
- Sur tous les clients, la qualité du tri bouge à peine du niveau 0 au niveau 3 (ratio d'aire de CatBoost : 0,569 et 0,566).
- Les deux essais n'ont ni le même périmètre ni les mêmes plis : l'écart mêle le changement de périmètre et les corrections des codifications.
- L'apport du nettoyage est ailleurs : les codifications corrigées (codifications 1 de septembre, codifications 2 d'avril à juin) sur lesquelles reposent les deux règles métier, qui retiennent des clients que la codification brute de la banque laisse passer (H10).

### H8. Plus de variables ne fait pas un meilleur modèle : à score égal, le plus simple ✅

- Du scénario complet (`ml_2`, 53 variables) à la version finale (21 variables), tous les scénarios restent dans le bruit : score décisionnel F2 de CatBoost entre 0,446 et 0,453 (page 6.3).
- Version finale `ml_17` : 21 variables, le niveau d'études pour seule donnée démographique ; l'âge, le genre et le statut marital ont été retirés sans perte.
- Le meilleur score parmi des candidats à égalité est biaisé vers le haut (piège du gagnant) : à égalité, on garde le plus simple.

---

## 3. Les populations à risque : population en incident et retard imminent

### H9. Déclarer ces deux populations en défaut de paiement est la seule décision défendable avec ces données ✅

- Sur le niveau 3 du nettoyage, la population en incident à M compte 3 754 clients, en défaut de paiement à 59,2 % ; le retard imminent, 989 clients, à 65,6 % (`essai_jeu_corrige_deux_populations.ipynb`, section 1).
- Avec une exigence métier stricte (on ne sort un client de ces populations que s'il a au moins 9 chances sur 10 d'être sans défaut de paiement), tous les modèles, dans les trois variantes, gardent la quasi-totalité des clients en défaut (rappel de 99 à 100 %) ; ils y trient à peine mieux que le hasard (ROC AUC de 0,59 à 0,64 en incident, de 0,53 à 0,63 en retard imminent ; section 3).
- Rien dans les paiements ne distingue les clients en incident qui paieront (H3).
- Un seul modèle, sans séparation, laisse partir 391 défauts de paiement de ces populations (2 480 détectés sur 2 871) et n'en trouve que 47 ailleurs (section 8 ; page 8.1, sous-partie 3).
- Hors des règles, la règle « 1 pour 1 » ne signale presque personne (moins de 1 % des défauts des autres clients) : chez eux, presque aucun client n'a plus d'une chance sur deux d'être en défaut de paiement (section 3).

### H10. Règles métier et codification de la banque : deux points de la même courbe ✅

Sur les mêmes 28 851 clients du niveau 3 (`essai_jeu_de_base_deux_populations.ipynb`, section 6) :

| Stratégie | Séparation | Défauts détectés | Précision | Fausses alertes | Taux d'erreur | Ratio d'aire |
|---|---|---|---|---|---|---|
| Règle seule | Banque (`PAY_1` ≥ 2, jeu de base) | 2 169 (34,6 %) | 69,5 % | 951 | 0,175 | 0,324 |
| Règle seule | Règles métier (jeu corrigé) | 2 871 (45,8 %) | 60,5 % | 1 872 | 0,183 | 0,394 |
| Règle + modèle | Banque | 2 403 (38,3 %) | 66,8 % | 1 193 | 0,175 | 0,565 |
| Règle + modèle | Règles métier | 2 871 (45,8 %) | 60,5 % | 1 874 | 0,183 | 0,550 |

- Les deux séparations se recouvrent en partie : les 989 clients en retard imminent et 2 131 des 3 754 clients en incident ont aussi `PAY_1` ≥ 2 dans les données d'origine ; les 1 623 autres clients en incident ont une codification de septembre d'origine sous 2, que les règles lisent corrigée (page 3.5).
- Les règles métier trouvent plus de défauts de paiement (45,8 % contre 34,6 %), avec une précision plus basse (60,5 % contre 69,5 %) : à la marge, les clients qu'elles ajoutent sont en défaut de paiement un peu moins d'une fois sur deux. Une fois le modèle ajouté et lu par niveaux de risque, c'est un autre point de la même courbe (H11).
- **La valeur des règles métier n'est pas le score** : elles sont justifiées et explicables (deux codifications de retard d'affilée, ou une seule de 3 ou plus, lues sur les codifications corrigées), là où `PAY_1` ≥ 2 retient aussi des retards isolés et laisse passer les codifications 1. La comparaison mêle la règle et le nettoyage : elle répond à « tout le travail fait-il mieux que la codification de la banque ? ».

### H11. Toutes les approches tombent sur la même courbe de niveaux de risque ✅

Niveaux de risque (règle, puis haut risque jusqu'à 30 % des défauts des autres clients, très haut risque compris, puis risque modéré jusqu'à 60 %), sur les 27 202 clients du périmètre, chaque client classé par un modèle qui ne l'a pas vu (`comparatif_global/niveaux_de_risque_global.ipynb` ; page 8.1) :

| Approche | Règle seule | + haut risque | + risque modéré |
|---|---|---|---|
| Version finale : règles métier, puis `ml_17` | 48,1 % des défauts, précision 60,5 % | 63,8 %, 48,1 % | 78,8 %, 36,4 % |
| Règles métier, puis un modèle sur les 23 variables d'origine | 48,1 %, 60,5 % | 63,4 %, 48,9 % | 78,2 %, 36,0 % |
| Règles métier, puis un modèle sans aucune codification | 48,1 %, 60,5 % | 63,1 %, 47,7 % | 78,1 %, 35,5 % |
| Codification de la banque (`PAY_1` ≥ 2), puis un modèle sur les 23 variables d'origine | 36,3 %, 69,5 % | 54,2 %, 58,2 % | 71,4 %, 41,2 % |
| Codification de la banque, puis un modèle sans aucune codification | 36,3 %, 69,5 % | 53,2 %, 56,2 % | 71,5 %, 40,4 % |

- **Le travail sur les variables n'a pas déplacé la courbe** : la version finale fait comme un modèle sur les 23 variables d'origine, à chaque palier (H1, H7).
- **Les règles métier et la codification de la banque se valent** : la codification de septembre retient moins de clients, avec plus de précision, mais trouve moins de défauts de paiement ; une fois le modèle ajouté, c'est un autre point de la même courbe (H10).
- **Le comportement seul fait presque aussi bien** : sans aucune codification, le modèle trouve autant de défauts de paiement, pour une précision à peine plus basse (H6).
- **Évaluation finale** : sur le test, jamais vu, les taux par tranche restent proches de ceux du train hors pli (première tranche 46,1 % contre 40,4 %, dernière tranche signalée 13,9 % contre 16,9 %, non signalés 9,4 % contre 8,7 %) : la courbe est celle du portefeuille (`evaluation_finale_test.ipynb`, section 6).
- **Sur des clients jamais vus** (les 5 441 clients des démonstrations : test du ML et 20 % de chacune des deux populations des règles), le système du projet et un modèle lancé sur les 23 variables d'origine trouvent presque autant de défauts de paiement avec le même nombre d'alertes ; l'avance du modèle brut au premier palier vient de clients des règles qu'il laisse partir (page 8.1, sous-partie 3, calculé en direct).
- **Niveaux présentés sur le site** (tout le périmètre, `evaluation_finale_test.ipynb`, section 6, tranches regroupées comme sur les pages 6.4 et 8.4) : très haut risque 41,6 % de défaut de paiement, haut risque 25,7 %, risque modéré 17,9 %, risque faible 8,9 %.

### H12. Les corrélations de l'EDA sont réelles, mais elles distinguent des groupes, pas des individus ✅

- L'EDA montre de vrais écarts de taux de défaut entre groupes (retards passés, plafond, utilisation du plafond) ; le modèle les retrouve : du risque faible (8,9 %) au très haut risque (41,6 %), un écart de 1 à 5, stable du train au test (H11).
- Mais même la tête de liste compte une majorité de clients qui paient : les corrélations rangent bien les clients par niveau de risque, sans désigner lequel fera défaut. Fort entre groupes, faible au client près : le cas classique du risque de crédit.
- Les colonnes construites n'ont pas amélioré le score du meilleur modèle. Deux raisons possibles, impossibles à départager : l'information était déjà dans les montants et les codifications d'origine, que le modèle combine lui-même ; ou le signal (comportement inhabituel, rupture) était trop rare, trop faible ou sans lien avec la cible. Les colonnes construites restent utiles pour **décrire** le risque d'un groupe. La démographie a un lien réel mais faible et redondant avec le comportement : l'élagage n'en a gardé que le niveau d'études.
- **Réponse à la problématique** : le comportement du client explique une partie du défaut de paiement, à l'échelle des groupes ; il ne suffit pas à prédire le défaut de chaque client avec certitude.

### H13. Les populations à risque gonflent les scores des jeux qui les contiennent ✅

- Sur tous les clients, populations des règles comprises, le tri atteint un ROC AUC d'environ 0,78 (ratio d'aire de 0,569 pour CatBoost sur le jeu de base, `essai_jeu_de_base.ipynb`) ; sur les seuls autres clients, 0,690 (`ml_17`, validation).
- Sur les mêmes autres clients, le jeu de base fait jeu égal avec la version finale (H6, H7) : l'écart venait des populations à risque, faciles à repérer (page 8.2).

---

## 4. Décisions de méthode issues de ces réflexions ⚙️

- **Taux de rappel minimal de 60 % dans les scénarios** : choix de départ, qui juge tous les modèles au même point. À ce point, la dernière tranche signalée (de 50 à 60 % des défauts) n'est en défaut de paiement qu'à 16,9 %, à peine plus que la moyenne des autres clients (13,8 %) ; et aucun seuil n'atteint 50 % de précision : même à 10 % des défauts, la précision est de 40,4 % (`evaluation_finale_test.ipynb`, sections 3 et 6).
- **Comparatif global** :
  - critère des réglages : la précision moyenne, qui juge le tri sur tous les rappels ;
  - seuil de décision par la **règle marginale** : signaler un client tant que les derniers signalés valent la peine (gain net « défauts détectés − tolérance × bons clients signalés »). C'est la règle de décision à coûts fixés : elle ne dépend pas du taux de défaut, seulement du coût des erreurs ;
  - **le F2 maximal est écarté** : il s'arrête quand la précision marginale tombe à F2 / 5, soit environ 1 défaut pour 7 bons clients ; avec 22 % de défauts, signaler tout le monde donne déjà un F2 d'environ 0,59 ;
  - **un plancher sur la précision moyenne est écarté** : il laisse passer, à la marge, des clients bien moins souvent en défaut que le plancher ;
  - **tolérance par population, fixée par le coût de l'erreur** : 1 bon client signalé pour 1 défaut chez les autres clients ; dans les populations des règles, on ne sort un client que s'il a au moins 9 chances sur 10 d'être sans défaut de paiement, car sortir à tort un client qui ne paiera pas abandonne une créance.
- **Un seul modèle, une seule règle** : sans séparation, les populations des règles n'existent pas ; le modèle unique répond à « qui paiera ou ne paiera pas ? », avec la même exigence pour tous. L'écart avec les stratégies séparées mesure l'effet de la séparation dans son ensemble (H9).
- **Puissance de la comparaison** : sur 5 plis, l'écart-type des gains pli par pli est de l'ordre de 0,005 à 0,01 en score décisionnel F2 (comparatif global, section 6) ; « dans le bruit » veut dire « pas démontré », pas « moins bon ». Pour un écart proche de ce bruit, mesurer plus finement (validation croisée répétée, test t corrigé de Nadeau et Bengio) plutôt que changer la règle après coup.
- **Règle de verdict à améliorer** : quand deux versions sont presque identiques, des écarts minimes, réguliers d'un pli à l'autre, peuvent donner un « gain réel » sans portée ; exiger aussi un gain minimal (par exemple 0,001) serait une nouvelle version de la méthode, non décidée.

---

## 5. Face à l'étude d'origine (Yeh et Lien, 2009)

- L'étude ne publie ni ROC AUC ni rappel : seulement un taux d'erreur et un ratio d'aire (Tableau 1, p. 2477), sur un seul découpage. Son ratio d'aire vaut exactement 2 × ROC AUC − 1.
- **Qualité du tri** : légèrement meilleure ici. Ratio d'aire de 0,569 (jeu de base) et 0,566 (jeu corrigé) pour CatBoost, contre 0,54 pour leur meilleur modèle, le réseau de neurones (`essai_jeu_de_base.ipynb` et `essai_jeu_corrige.ipynb`, comparaison avec l'étude).
- **Le système du projet** (règles métier, puis `ml_17`), sur les 5 441 clients des démonstrations jamais vus : un ROC AUC d'environ 0,79, contre 0,77 pour l'étude : défi relevé, de peu (page 8.2, calculé en direct).
- **Taux d'erreur** : au même niveau, pas meilleur. 0,182 (jeu de base) et 0,181 (jeu corrigé) à la règle marginale, contre 0,17 pour leur réseau de neurones et 0,16 pour leur KNN.
- **Sans modèle**, les règles métier donnent déjà un taux d'erreur de 0,183 sur le niveau 3 (`essai_jeu_corrige_deux_populations.ipynb`, section 6) ; sur le fichier brut, la codification de la banque (`PAY_1` ≥ 2) donne 0,180 (ratio d'aire 0,308), et codification + modèle : taux d'erreur 0,181, ratio d'aire 0,564, **sur le même périmètre que l'étude** (`essai_jeu_de_base_deux_populations.ipynb`, section 5).
- L'article contient des incohérences (25 000 observations annoncées pour 30 000 dans le fichier ; 22,12 % de défauts puis 87,88 % de clients sans risque).

**À dire dans la conclusion, avant tout chiffre** : la comparaison avec l'étude ne peut pas être exacte, pour trois raisons.
- **Leur objectif n'était pas le nôtre.** L'étude cherche d'abord à **bien estimer la probabilité de défaut** (sa méthode de lissage, *Sorting Smoothing Method*, et la régression entre probabilité estimée et « vraie » probabilité, R² de 0,965 pour le réseau de neurones) et à **bien trier** les clients (ratio d'aire). Elle ne cherche pas à **détecter** un maximum de défauts à un seuil choisi : elle ne publie ni rappel ni précision, et son taux d'erreur suppose un seuil qu'elle ne décrit pas. Nos modèles sont réglés pour détecter (précision au taux de rappel minimal, ou règle marginale) et pondèrent les défauts : leurs probabilités sont décalées vers le haut, donc mal calibrées au sens de l'étude.
- **Les modèles ont progressé depuis.** Le réseau de neurones de l'étude est un réseau à rétropropagation de 2006-2007 : l'étude est publiée en 2009, mais menée avant (son texte parle du pic des impayés « attendu » au troisième trimestre de 2006, et l'article est enregistré par l'éditeur dès la fin de 2007, doi:10.1016/j.eswa.2007.12.020) ; les modèles de boosting d'arbres utilisés ici (CatBoost, comme XGBoost et LightGBM) sont apparus après (années 2016 à 2018), avec la validation croisée et la recherche automatique de réglages devenues courantes. Que notre meilleur modèle trie un peu mieux (ratio d'aire) est attendu ; que l'écart reste faible confirme que la limite vient des données (H1).
- **Nos traitements diffèrent des leurs, sans que l'on connaisse les leurs en détail** : un seul découpage chez eux (proportions non précisées, environ la moitié des clients en validation d'après leurs courbes de gain), une validation croisée à 5 plis ici ; réglages, mise à l'échelle et traitement du déséquilibre non décrits chez eux ; ici, logarithme des montants, pondération des défauts, contrôle du surapprentissage, retrait des deux populations des règles (version finale) ou séparation par les règles (comparatif global).

---

## 6. Ce que je referais autrement (leçons de méthode)

La méthode a été rigoureuse (aucune règle ni seuil optimisé sur la cible, test lu une seule fois et confirmant la validation, tout tracé et reproductible) et le résultat de fond n'aurait sans doute pas changé. Le chemin aurait pu être plus court :
1. **Estimer tôt le bruit qui reste dans le périmètre retenu.** Le bruit visible de la cible (des clients sans dette comptés en défaut) a été écarté dès le départ, par le périmètre des clients qui ont une dette en septembre. Ce qui n'a été mesuré qu'à la fin, c'est la part de défauts imprévisibles **restant** dans ce périmètre (environ un quart, H2) : l'estimer dès les premiers scénarios aurait annoncé le plafond.
2. **Calculer ce que la comparaison peut détecter avant d'ajouter les colonnes une à une.** Avec 5 plis, le bruit des gains est de l'ordre de 0,005 à 0,01 en score décisionnel F2 : presque tous les ajouts de la première itération sont tombés dans le bruit. La deuxième itération est partie du scénario complet pour élaguer ensuite, ce qui a été plus rapide ; mesurer finement (validation croisée répétée) dès le départ l'aurait été plus encore.
3. **Comparer dès le départ au socle des variables d'origine, et décider du point de fonctionnement à la fin.** Un modèle sur les 23 variables d'origine fait jeu égal avec la version finale (H1, H7), et toutes les approches tombent sur la même courbe (H11) : le comparer d'abord, sur une mesure sans seuil comme la précision moyenne, aurait montré plus tôt que les colonnes construites n'apportent rien au score. La règle de décision (taux de rappel minimal, règle marginale, niveaux de risque) se choisit ensuite, avec la banque ; la règle « 1 pour 1 », qui ne signale presque aucun des autres clients, aurait été une mauvaise mesure de comparaison.
4. **Refaire une exploration courte sur la population du ML, une fois les deux populations des règles retirées.** Faite à la fin (`eda_population_ml.ipynb` ; page 6.5), elle montre que certains liens de l'exploration s'effacent sur cette population (le type d'usage ne distingue presque plus les clients : de 13,2 à 14,0 % de défaut pour les types les plus courants), que d'autres tiennent (plafond : 19,9 % de défaut jusqu'à 50 000 NT$, 7,9 % de 300 000 à 500 000 NT$) et que les retards passés restent le signal le plus fort (de 11,1 % sans aucun mois en retard à 52,2 % pour cinq mois). Les liens qui tiennent sont ceux que garde la version finale : faite avant les scénarios, elle aurait annoncé quelles colonnes avaient une chance d'aider.
5. **Appliquer la règle « à score égal, le plus simple » au choix du modèle, pas seulement aux variables.** Dans `ml_17`, les cinq modèles sont à égalité (CatBoost 0,451, régression logistique 0,448, dans le bruit) ; CatBoost a été désigné parce qu'il était en tête, ce qui revient au piège du gagnant (H8). À égalité, la régression logistique, plus simple et plus explicable (un poids lisible par variable, justifiable devant la gestion des risques), aurait été le choix cohérent. Choix fixé avant la lecture du test, non revu ensuite (sur le test : 0,426 contre 0,434, toujours dans l'incertitude ; `evaluation_finale_test.ipynb`, section 4) ; dit aussi sur le site (page 6.6).
6. **La calibration**, objectif principal de l'étude d'origine, n'a pas été traitée : mise de côté (probabilité de défaut de paiement par client : piste ouverte, page 8.5).

## 7. Ce qui manque pour aller plus loin (ouverture)

- **La définition exacte de `dpnm`** : défaut de paiement observé ou statut posé par la banque (H3).
- **Les vrais encours** : `BILL_AMT` est le montant du relevé, qui ne serait pas toujours la dette réelle (certains défauts chez des clients sans dette affichée le laissent penser). Avec l'encours réel, on saurait si les clients « sans dette » l'étaient vraiment, et si leur défaut est du bruit de la cible ou une dette invisible dans les relevés.
- **La liste des clients suivis hors du circuit normal** (recouvrement, contentieux) : elle validerait les deux règles métier (clients retrouvés, manqués, ajoutés à tort) et séparerait le défaut « administratif » du vrai impayé, là où se cache probablement le quart de défauts imprévisibles (H2).
- **La façon dont l'échantillon a été tiré** : avec environ un client sur cinq en défaut de paiement, il ne ressemble pas à un portefeuille réel ; savoir quels clients ont été retenus dirait si la sélection a rendu la tâche plus difficile (H4).

**Conclusion provisoire** : on a tiré de ces données ce qu'elles contiennent, et on sait mesurer ce qu'elles ne contiennent pas. Nettoyer davantage les variables selon des règles métier transformerait le jeu en notre propre lecture ; recoder la cible changerait la question (les modèles prédiraient notre définition du défaut de paiement). La suite logique dépasse ce jeu de données : obtenir les données manquantes ci-dessus.

---

## 8. Tests à mener (issus de ces hypothèses)

| Test | Hypothèse | État |
|---|---|---|
| Taux de défaut des clients sans dette et des clients en incident qui paient, recalculés dans un notebook | H3 | fait : `lab_ML/eda_population_ml.ipynb`, sections 5 et 6 |
| Lire les populations des règles dans `essai_jeu_corrige_deux_populations.ipynb` : variante « sans les `PAY_n` », importance par famille | H9 | fait |
| Comparer la séparation par les règles métier à celle de la banque (`PAY_1` ≥ 2), sur les clients communs | H10 | fait : deux points de la même courbe |
| Ajouter la stratégie « un seul ML » aux deux synthèses (cellules d'enregistrement des essais à un seul modèle, puis synthèse) | H5, H9 | fait |
| Règle de verdict avec un gain minimal | méthode | à décider |
| Mesurer la calibration à la manière de l'étude (lissage, régression probabilité estimée / « vraie », R²) sur les probabilités hors pli, éventuellement après calibration des modèles : comparaison sur leur objectif principal | section 5 | piste, non lancée |
